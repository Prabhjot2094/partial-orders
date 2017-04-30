import robot

class LambdaPi(robot.Robot):
    def processFromSonar():
        global sensorData
        global prevX
        global prevY
        global prevUS
        global turningFlag
        global turnFlag

        sensorData[-1] = [(207.0,133),(207.0,102),(121,199)]
        if turnFlag is True and turningFlag is False:
            turningFlag = True
            sensorData[-2] = [(prevX,prevY)]
            print "turn = %s, turning = %s"%(turnFlag,turningFlag)
            return

        elif turnFlag is False and turningFlag is True:
            turningFlag = False
            sensorData[-2] = [(prevX,prevY)]
            prevUS = float(sensorData[US_INDEX])
            print sensorData
            print "turn = %s, turning = %s"%(turnFlag,turningFlag)
            return
        
        if prevX is None and prevY is None:
            prevUS = float(sensorData[US_INDEX])
            if prevUS == 0:
                prevUS = None
                sensorData[-2] = [(0,0)]
                return
            sensorData[-2] = [(0,0)]
            prevX = prevY = 0
            print sensorData
            return

        currentYaw = float(sensorData[YAW_INDEX])
        currentDistance = float(sensorData[US_INDEX])

        if currentDistance == 0:
            sensorData[-2] = [(prevX,prevY)]
            return
        
        distanceDiff = prevUS - currentDistance

        if abs(distanceDiff) > MAX_DISTANCE_DIFF:
            sensorData[-2] = [(prevX,prevY)]
            prevUS = currentDistance
            return

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
        prevUS = currentDistance
    
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
        initialtime = time.time()

        try:
            dataReadThread = threading.Thread(target=readSensorData)
            dataReadThread.setDaemon(True)
            dataReadThread.start()
        except Exception as e:
            print "Exception in dataReadThread " + str(e)
            shutdown()

#        drive('stop', 255, False)
#        while True:
#            time.sleep(0.01)

    except KeyboardInterrupt:
        shutdown()

    except Exception as e:
        print "Exception in main " + str(e)
        shutdown()
        raise

