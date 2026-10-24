# ESP32 + MPU6050 IMU (steps + heading) — Wokwi virtual test

Part of the **BLE Indoor Navigation Beacon System** virtual prototype. This module tests the IMU part of the mobile gateway on a virtual ESP32 (Wokwi) before the real hardware is built. The sketch reads an MPU6050 and prints three values on the Serial Monitor:

- `acc` – total acceleration (m/s²)
- `heading` – how far the board has turned since start (degrees)
- `steps` – number of detected steps

> Wokwi does not reliably simulate BLE, so this test covers only the IMU + Serial part. The BLE/RSSI part needs real boards or a software model.

## Files

| File | Purpose |
|---|---|
| `diagram.json` | Circuit: ESP32 DevKit V1 + MPU6050 + wires (+ Serial Monitor link) |
| `libraries.txt` | Tells Wokwi to install the `Adafruit MPU6050` library |
| `sketch.ino` | ESP32 program (reads the sensor, computes heading and steps) |

## Wiring

| MPU6050 | ESP32 (DevKit V1) | Note |
|---|---|---|
| VCC | 3V3 | ESP32 logic is 3.3 V, so power the sensor from 3V3 |
| GND | GND | |
| SDA | D21 (GPIO21) | default I2C data pin |
| SCL | D22 (GPIO22) | default I2C clock pin |
| AD0 | not connected | I2C address 0x68 (AD0 to VCC would give 0x69) |
| INT, XDA, XCL | not connected | not used |

## Run it in Wokwi

1. Open wokwi.com → **New Project** → ESP32 (Arduino).
2. Replace the content of `diagram.json` with the file from this folder.
3. Put `Adafruit MPU6050` in `libraries.txt` (or add it through the Library Manager, which creates the file).
4. Paste `sketch.ino`.
5. Press ▶ and open the Serial Monitor.

If compilation fails with a missing `Adafruit_BusIO` or `Adafruit_Sensor.h`, add two more lines to `libraries.txt`: `Adafruit BusIO` and `Adafruit Unified Sensor`.

Expected output (about 10 lines per second):

```
IMU ready
acc=9.81 m/s2  heading=0.0 deg  steps=0
```

## How the sketch works

| Code | What it does |
|---|---|
| `Wire.begin(21, 22)` | starts the I2C bus on GPIO21 (SDA) and GPIO22 (SCL) |
| `while (!mpu.begin())` | looks for the MPU6050 at 0x68; prints a message every second until found |
| `mpu.getEvent(&a, &g, &temp)` | reads acceleration (m/s²), rotation speed (rad/s) and temperature |
| `dt` | seconds since the previous loop |
| `heading += g.gyro.z * 57.2958 * dt` | rotation speed × time = angle turned (57.2958 = 180/π converts radians to degrees) |
| `mag = √(x² + y² + z²)` | total acceleration (gravity + motion); same for any board orientation |
| `mag > 11.5 && now - lastStepMs > 300` | a step = an acceleration spike, at least 300 ms after the previous step |
| `printf` + `delay(100)` | prints the three values about 10 times per second |

`heading` is relative to the start direction (there is no compass/magnetometer) and it does not wrap at 360°.

## Why `acc ≈ 9.81`, `heading 0.0`, `steps 0` at rest

- **acc ≈ 9.81 m/s²** – an accelerometer also measures gravity. A board lying still feels 1 g (9.80665 m/s²), so the reading is not zero. In Wokwi the default is `accelZ = 1` (g) and X = Y = 0, so √(0² + 0² + 9.81²) = 9.81. Tilting the board spreads gravity over X, Y and Z, but the total stays 9.81.
- **heading 0.0** – heading is the running sum of (rotation speed × time). With gyro Z = 0 there is nothing to add, so it stays at its start value 0.
- **steps 0** – a step is counted only when `acc` rises above 11.5 m/s² (≈ 1.17 g). At 9.81 it never does.

## Changing the values in Wokwi

While the simulation runs, click the MPU6050 part to open its controls. Units: acceleration in **g**, rotation in **°/s**. (Initial values can also be set in `diagram.json` → `attrs`: `accelX/Y/Z`, `rotationX/Y/Z`.)

Important: Wokwi `accelZ` is in **g**, the sketch threshold is in **m/s²**. 11.5 m/s² ≈ 1.17 g, so use e.g. `accelZ = 1.3`, not 12.

| Set | Expected Serial output (approx.) |
|---|---|
| `accelZ = 1`, `rotationZ = 0` (default) | acc 9.81, heading 0.0, steps 0 |
| `rotationZ = 90` | heading +9° per line (~90° per second); stops changing when set back to 0 |
| `rotationZ = -90` | heading decreases, about −9° per line |
| `accelZ = 1.3` | acc 12.75; steps +1 about every 0.3 s (≈ 3 per second) |
| `accelZ = 1` again | steps stop increasing |

Turn direction: with the board flat (Z axis up), a left turn (counter-clockwise seen from above) is positive rotation Z, so heading increases.

The slider holds a constant value, not a real walking waveform. So steps keep increasing for as long as `accelZ` stays above ~1.17 g. This is a logic test, not a gait simulation.

### Walk around a room with 4 corner beacons (B1 → B2 → B3 → B4)

Start near B1, facing B2 (heading 0).

| Do | Serial shows (approx.) |
|---|---|
| Wall B1→B2: `accelZ = 1.3` for ~1.5 s, then 1 | steps ≈ 5, heading 0 |
| Corner B2, turn left: `rotationZ = 90` for ~1 s, then 0 | heading ≈ 90 |
| Wall B2→B3: `accelZ = 1.3` for ~1.5 s, then 1 | steps ≈ 10 |
| Corner B3, turn left: `rotationZ = 90`, then 0 | heading ≈ 180 |
| Wall B3→B4, corner B4 | steps ≈ 15, heading ≈ 270 |
| Wall B4→B1, corner B1 | steps ≈ 20, heading ≈ 360 |

Tips:
- Stop `rotationZ` by watching `heading` in the Serial Monitor, not a stopwatch. A 1 s turn lands anywhere between ≈ 83° and 92° because the loop runs every ~0.1 s. A slower rate (e.g. 30 °/s) is more precise.
- The Wokwi MPU6050 controls can also be scripted with Wokwi Automation Scenarios.

The numbers in this README come from an offline model of the sketch (loop ≈ 102 ms). Values in Wokwi can differ slightly.

## On a real ESP32

Use the same wiring and sketch; set the Serial Monitor to 115200 baud. Most GY-521 MPU6050 boards already have a regulator and I2C pull-ups, so the four wires are enough. Values now come from real motion instead of sliders, but expect these differences:

1. **No exact 9.81 / 0.0 at rest.** `acc` hovers around 9.8, and the gyro has a small offset, so `heading` slowly drifts.
2. **Keep the board flat** (Z axis up). Heading only uses the Z gyro; a tilted board gives wrong headings.
3. **Tune the 11.5 threshold.** Step spikes depend on how the device is carried (hand, pocket, bag). Walk, print `acc`, and adjust.
4. **Heading is relative.** Define it yourself, e.g. 0° = direction from B1 to B2.
5. **Wrong turn direction?** If a left turn decreases `heading`, the board is mounted the other way; use `heading -=`.

Gyro offset calibration + 0–360° wrap (call `calibrateGyro();` in `setup()` after `mpu.begin()`):

```cpp
float gyroBias = 0;                       // rad/s

void calibrateGyro() {                    // keep the board perfectly still for ~2 s
  float sum = 0;
  for (int i = 0; i < 200; i++) {
    sensors_event_t a, g, t;
    mpu.getEvent(&a, &g, &t);
    sum += g.gyro.z;
    delay(10);
  }
  gyroBias = sum / 200;
}

// in loop(), replace the heading line with:
heading += (g.gyro.z - gyroBias) * 57.2958 * dt;
if (heading >= 360) heading -= 360;
if (heading < 0)    heading += 360;
```

(With the wrap, a full lap shows ≈ 0° instead of 360°.)

## How this fits the 4-corner beacon system

The IMU gives *relative* motion. With step length `L` (about 0.7 m; measure it by walking 10 steps) and heading `θ` (counter-clockwise from the +x axis):

```
x += L · cos(θ)
y += L · sin(θ)
```

This is smooth but drifts over time. BLE RSSI from the 4 corner beacons gives an *absolute* position by trilateration, but it is noisy. Combining the two (sensor fusion) is the next stage. The sketch does not compute x, y yet.

## Troubleshooting

| Problem | Fix |
|---|---|
| Compile error about `Adafruit_BusIO` / `Adafruit_Sensor.h` | add `Adafruit BusIO` and `Adafruit Unified Sensor` to `libraries.txt` |
| "MPU6050 nahi mila - wiring check karo!" repeats | `diagram.json` not applied, or a wire is missing: check VCC/GND/SDA/SCL |
| Steps never increase | `accelZ` must be above ~1.17 g (it is in g, not m/s²) |
| Steps keep increasing | expected while `accelZ` stays above the threshold; set it back to 1 |
| Heading drifts on the real board | run `calibrateGyro()` with the board still |
| Numbers differ slightly from this README | normal; they depend on loop timing |
