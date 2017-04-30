import robot

class LambdaPi(robot.Robot):
    
    prevX,prevY = 0,0
    x,y = None,None
    prevUS = None
    turningFlag = False
    turnFlag = False
    referenceYaw = None
    ROBOT_SPEED = None
    autopilotStartTime = None

    def processFromSonar():
        sensorData = self.sensorData
        prevX,prevY = self.prevX, self.prevY
        x,y = self.x, self.y
        prevUS = self.prevUS
        turningFlag = self.turningFlag
        turnFlag = self.turnFlag
        referenceYaw = self.referenceYaw
        ROBOT_SPEED = self.ROBOT_SPEED
        autopilotStartTime = self.autopilotStartTime

        if prevX is None and prevY is None:
            prevUS[0] = float(sensorData[US_INDEX])
            if prevUS[0] == 0:
                prevUS = [None,None]
                sensorData[-2] = [(0,0)]
                return
            
            referenceYaw = float(sensorData[YAW_INDEX])
            print "Ref Yaw"
            print referenceYaw

            sensorData[-2] = [(0,0)]
            prevX = prevY = 0
            return
        
        if turnFlag is True and turningFlag is False:
            turningFlag = True
            sensorData[-2] = ["Turn Start"]
            #print "turn = %s, turning = %s"%(turnFlag,turningFlag)
            #print prevUS
            #print sensorData
            return

        elif turnFlag is False and turningFlag is True:
            turningFlag = False
            sensorData[-2] = ["Turn End"]
            prevUS[1] = None
            prevUS[0] = float(sensorData[US_INDEX])
            #print "turn = %s, turning = %s"%(turnFlag,turningFlag)
            #print prevUS
            #print sensorData
            #currentYaw = getYawReference(float(sensorData[YAW_INDEX]))
            #x -= math.cos(math.radians(currentYaw))*ROBOT_SPEED*0.7
            #y -= math.sin(math.radians(currentYaw))*ROBOT_SPEED*0.7
            autopilotStartTime = time.time()
            return

        currentYaw = float(sensorData[YAW_INDEX])
        print currentYaw
        currentYaw = getYawReference(currentYaw)
        
        distance = ROBOT_SPEED*(time.time()-autopilotStartTime)
        autopilotStartTime = time.time()

        localX = math.cos(math.radians(currentYaw))*distance
        localY = math.sin(math.radians(currentYaw))*distance

        x+=localX
        y+=localY
        
        sensorData[-1] = [(x,y)]
        #print currentYaw
        #print sensorData[-1]

        currentDistance = float(sensorData[US_INDEX])

        distanceDiff = prevUS[0] - currentDistance
        
        if currentDistance == 0:
            sensorData[-2] = [(prevX,prevY)]
            print "Distance 0"
            print prevUS
            print sensorData
            return
       
        if distanceDiff > MAX_DISTANCE_DIFF or distanceDiff < 0:
            if prevUS[1] == None:
                sensorData[-2] = [(prevX,prevY)]
                prevUS[1] = prevUS[0]
                prevUS[0] = currentDistance
                print "distanceDiff > MaxDistance or distnace diff = 0"
                print prevUS
                print sensorData
                return
            else:
                correctUS = [prev_us-currentDistance if prev_us>currentDistance else 999 for prev_us in prevUS]
                distanceDiff = min([i for i in correctUS])
                pos = [prev_us for prev_us in correctUS].index(distanceDiff)

                if distanceDiff > MAX_DISTANCE_DIFF :
                    sensorData[-2] = [(prevX,prevY)]
                    prevUS[1] = prevUS[0]
                    prevUS[0] = currentDistance

                    print "DistnaceDiff from both prev is greater than max Distance"
                    print prevUS
                    print sensorData
                    return
                prevUS[1] = prevUS[pos]
                prevUS[0] = currentDistance
        
        localX = math.cos(math.radians(currentYaw))*distanceDiff
        localY = math.sin(math.radians(currentYaw))*distanceDiff

        '''
        tempX = prevX + localX
        tempY = prevY + localY
        distance = math.hypot(tempX-prevX, tempY-prevY)
        if distance > MAX_DISTANCE_DIFF :
            sensorData[-2] = prevX
            sensorData[-1] = prevY
            return
        '''

        prevX += localX
        prevY += localY

        sensorData[-2] = [(prevX,prevY)]
        print "New Points"
        print prevUS
        print sensorData
        prevUS[1] = prevUS[0]
        prevUS[0] = currentDistance

    
    def autopilot(type='sonar', speed=255):
        global autopilotFlag
        global sensorDataQueue
        global turnFlag

        lock = threading.Lock()

        if type == 'sonar-yaw':
            robotPID = PID.PID(YAW_P, YAW_I, YAW_D)
            robotPID.setPoint = getSensorData()[YAW_INDEX]
            robotPID.setSampleTime(PID_UPDATE_INTERVAL)

        while True:
            if autopilotFlag:
                sensorData = getSensorData()

                if not VERBOSE_DATA_REPORTING:
                    dataProcessor()
                    sensorDataQueue.put(sensorData)

                if type == 'sonar':
                    obstacleArray = []
                    obstacle = checkObstacle(sensorData, obstacleArray)

                    if obstacle == 100:     # no obstacle
                        writeMotorSpeeds(speed, speed)
                        time.sleep(0.01)
                    elif obstacle < 0:      # obstacle towards left
                        turnFlag = True
                        writeMotorSpeeds(speed, -speed)
                        
                        lock.acquire()
                        print sensorData
                        dataProcessor()
                        lock.release()
                        
                        time.sleep(.700)
                        writeMotorSpeeds(0, 0)
                        turnFlag = False
                    elif obstacle >= 0:     # obstacle towards right or in front
                        turnFlag = True
                        
                        lock.acquire()
                        print sensorData
                        dataProcessor()
                        lock.release()
                        
                        writeMotorSpeeds(-speed, speed)
                        time.sleep(.700)
                        writeMotorSpeeds(0, 0)
                        turnFlag = False

                elif type == 'sonar-yaw':
                    obstacleArray = []
                    obstacle = checkObstacle(sensorData, obstacleArray)

                    if obstacleArray[2] == 0:
                        writeMotorSpeeds(0, 0)

                    elif obstacle == 100:
                        feedback = sensorData[YAW_INDEX] - robotPID.setPoint

                        if feedback < -180.0:
                            feedback += 360
                        elif feedback > 180:
                            feedback -= 360

                        robotPID.update(feedback)
                        pidOutput = int(robotPID.output)

                        if pidOutput < 0:
                            writeMotorSpeeds(MAX_SPEED + pidOutput, MAX_SPEED)      # turn left if PID output is -ve
                        else:
                            writeMotorSpeeds(MAX_SPEED, MAX_SPEED - pidOutput)      # turn right if PID output is +ve

                    elif obstacle < 0:
                        robotPID.setPoint += TURN_ANGLE
                        if robotPID.setPoint > 180:
                            robotPID.setPoint -= 360

                        writeMotorSpeeds(speed, -speed)
                        while (robotPID.setPoint - getSensorData()[YAW_INDEX])  > 10:
                            pass
                        else:
                            writeMotorSpeeds(0, 0)

                    else:
                        robotPID.setPoint -= TURN_ANGLE
                        if robotPID.setPoint < -180:
                            robotPID.setPoint += 360

                        writeMotorSpeeds(-speed, speed)
                        while getSensorData()[YAW_INDEX] - robotPID.setPoint > 10:
                            pass
                        else:
                            writeMotorSpeeds(0, 0)

            else:
                writeMotorSpeeds(0, 0)
                print "Autopilot Stopped"
                return

def main():
    try:
        lambdaPi = LambdaPi()
        initialtime = time.time()

        try:
            dataReadThread = threading.Thread(target=lambdaPi.readSensorData)
            dataReadThread.setDaemon(True)
            dataReadThread.start()
        except Exception as e:
            print "Exception in dataReadThread " + str(e)
            lambdaPi.shutdown()

        lambdaPi.drive('stop', 255, False)
        while True:
            time.sleep(0.01)

    except KeyboardInterrupt:
       lambdaPi.shutdown()

    except Exception as e:
        print "Exception in main " + str(e)
        lambdaPi.shutdown()
        raise

