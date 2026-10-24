float gyroBias = 0;                       // rad/s

void calibrateGyro() {                    // ~2 sec, board bilkul sthir
  float sum = 0;
  for (int i = 0; i < 200; i++) {
    sensors_event_t a, g, t;
    mpu.getEvent(&a, &g, &t);
    sum += g.gyro.z;
    delay(10);
  }
  gyroBias = sum / 200;
}

// loop() me heading wali line ki jagah:
heading += (g.gyro.z - gyroBias) * 57.2958 * dt;
if (heading >= 360) heading -= 360;
if (heading < 0)    heading += 360;
