# AGENTS.md

이 파일은 Codex 세션 시작 시 먼저 읽어야 하는 프로젝트 메모다.

## 세션 시작 규칙

새 Codex 세션에서 이 프로젝트를 다룰 때는 먼저 이 파일을 읽고, 이어서 다음 진행 지도를 읽는다.

```text
docs/roadmap.md
```

진행 중 새로 결정된 환경/명령/주의사항은 `AGENTS.md`에, 앞으로의 작업 순서와 체크리스트는 `docs/roadmap.md`에 갱신한다.

## 프로젝트 개요

프로젝트명: Robot Arm

목표:

- AX-12A DYNAMIXEL 기반 6서보 로봇팔 제어
- Jetson AGX에서 ROS2 상위 제어
- Raspberry Pi는 추후 모터 제어 서버로 사용
- 현재는 Jetson에서 AX-12A를 직접 제어하는 테스트까지 성공

GitHub:

```text
https://github.com/BONGMIN-AI/robot-arm-control
```

로컬 Windows 레포:

```text
C:\Users\kbm00\Documents\Codex\robot-arm-control
```

Jetson 레포 위치:

```text
~/robot-arm-control
```

## 하드웨어

- Jetson AGX
- Raspberry Pi 3, RAM 1GB, 추후 모터 제어 서버로 활용 예정
- DYNAMIXEL AX-12A 모터 6개
- DYNAMIXEL Wizard 2 사용
- 통신: 3핀 TTL Half-Duplex UART
- 프로토콜: DYNAMIXEL Protocol 1.0
- PWM 제어 사용하지 않음
- 모터 ID:
  - J0 = 0
  - J1 = 1
  - J2 = 2
  - J3 = 3
  - J4 = 4
  - J5 = 5

## 관절 의미

- J0: 베이스 yaw, +는 반시계
- J1: 어깨 pitch, +는 앞쪽으로 기울어짐
- J2: 팔꿈치 pitch, +는 앞쪽으로 기울어짐
- J3: 손목 pitch, +는 앞쪽으로 기울어짐
- J4: 그리퍼 roll, +는 반시계
- J5: 그리퍼 open/close, 위치 기구학에서는 제외

AX-12A 각도 기준:

```text
0..300 deg
150 deg = 홈/중앙
joint_angle = servo_angle - 150
```

## 좌표계

- x: 좌우 방향
- y: 로봇 앞 방향
- z: 바닥 기준 위 방향
- 측정점: 그리퍼 중앙

## 실측 치수

단위: mm

```text
B0 = 85   # 바닥에서 J0 회전 중심까지 높이
H0 = 49   # J0 회전 중심에서 J1 축 중심까지 높이
L1 = 109  # J1 축 중심에서 J2 축 중심까지 거리
L2 = 109  # J2 축 중심에서 J3 축 중심까지 거리
L3 = 63   # J3 축 중심에서 J4 축 중심까지 거리
L4 = 104  # J4 축 중심에서 그리퍼 중앙까지 거리
```

## 현재 주요 파일

```text
kinematics/dh_calculator.py              # 서보각 -> 그리퍼 x,y,z 예측
kinematics/joint_config.py               # 안전 관절 제한
kinematics/motion_plan.py                # 중간 각도 보간 경로 생성
raspberry_pi/ax12a_driver.py             # AX-12A Protocol 1.0 드라이버
raspberry_pi/move_once.py                # ROS2 없이 한 번 움직이는 테스트
ros2_ws/src/robot_arm_bringup/...        # ROS2 노드
docs/calibration.md                      # 캘리브레이션 기록
docs/safety.md                           # 안전 메모
```

## Jetson 환경

```text
Ubuntu 22.04.5 LTS jammy
aarch64
JetPack/L4T R36.4.3
ROS2 Humble ros-base 설치 성공
```

`ros-humble-desktop`은 처음에 의존성 문제로 막혔고, 현재 작업에는 `ros-base`로 충분하다.

## Jetson에서 로봇암 실행 순서

장치 포트 확인은 현재 폴더와 무관하다.

```bash
ls /dev/ttyUSB*
```

코드 업데이트 및 빌드:

```bash
cd ~/robot-arm-control
git pull
cd ~/robot-arm-control/ros2_ws
source /opt/ros/humble/setup.bash
export ROBOT_ARM_REPO=~/robot-arm-control
colcon build
source install/setup.bash
```

터미널 1에서 실제 제어 서버:

```bash
arm-real
```

터미널 2에서 목표각 전송:

```bash
arm-send 150 150 155 150 150 150
```

상태 읽기:

```bash
arm_status --device /dev/ttyUSB0
```

토크 제어:

```bash
arm_torque on --device /dev/ttyUSB0
arm_torque off --device /dev/ttyUSB0
```

주의: `arm_torque off`는 기본적으로 홈 자세 `150 150 150 150 150 150`으로 이동한 뒤 토크를 끈다.

현재 자세 저장:

```bash
arm_save_pose idle_01_a --device /dev/ttyUSB0
```

mock 상태 읽기:

```bash
arm_status --mock
```

홈 복귀:

```bash
arm-send 150 150 150 150 150 150
```

## Jetson alias

현재 사용 중인 alias는 `~/.bashrc`에 두는 방식이다.

다른 세션에서 Jetson alias를 다시 잡아야 하면 아래 블록을 그대로 복붙한다.  
포트가 `/dev/ttyUSB0`일 때 기준이다.

```bash
echo "alias arm-setup='cd ~/robot-arm-control && git pull && cd ros2_ws && source /opt/ros/humble/setup.bash && export ROBOT_ARM_REPO=~/robot-arm-control && colcon build && source install/setup.bash'" >> ~/.bashrc
echo "alias arm-real='cd ~/robot-arm-control/ros2_ws && source /opt/ros/humble/setup.bash && export ROBOT_ARM_REPO=~/robot-arm-control && source install/setup.bash && ros2 run robot_arm_bringup joint_command_listener --ros-args -p mock:=false -p device:=/dev/ttyUSB0 -p step_deg:=1.0 -p delay_sec:=0.08 -p speed:=50'" >> ~/.bashrc
echo "alias arm-send='cd ~/robot-arm-control/ros2_ws && source /opt/ros/humble/setup.bash && source install/setup.bash && ros2 run robot_arm_bringup send_joint_target'" >> ~/.bashrc
echo "alias arm-status='cd ~/robot-arm-control/ros2_ws && source /opt/ros/humble/setup.bash && export ROBOT_ARM_REPO=~/robot-arm-control && source install/setup.bash && ros2 run robot_arm_bringup arm_status --device /dev/ttyUSB0'" >> ~/.bashrc
echo "alias arm-torque='cd ~/robot-arm-control/ros2_ws && source /opt/ros/humble/setup.bash && export ROBOT_ARM_REPO=~/robot-arm-control && source install/setup.bash && ros2 run robot_arm_bringup arm_torque --device /dev/ttyUSB0'" >> ~/.bashrc
echo "alias arm-save-pose='cd ~/robot-arm-control/ros2_ws && source /opt/ros/humble/setup.bash && export ROBOT_ARM_REPO=~/robot-arm-control && source install/setup.bash && ros2 run robot_arm_bringup arm_save_pose --device /dev/ttyUSB0'" >> ~/.bashrc
source ~/.bashrc
```

등록 후 확인:

```bash
type arm-setup
type arm-real
type arm-send
type arm-status
type arm-torque
type arm-save-pose
```

현재 alias 내용만 임시로 다시 잡고 싶으면:

```bash
alias arm-setup='cd ~/robot-arm-control && git pull && cd ros2_ws && source /opt/ros/humble/setup.bash && export ROBOT_ARM_REPO=~/robot-arm-control && colcon build && source install/setup.bash'
alias arm-real='cd ~/robot-arm-control/ros2_ws && source /opt/ros/humble/setup.bash && export ROBOT_ARM_REPO=~/robot-arm-control && source install/setup.bash && ros2 run robot_arm_bringup joint_command_listener --ros-args -p mock:=false -p device:=/dev/ttyUSB0 -p step_deg:=1.0 -p delay_sec:=0.08 -p speed:=50'
alias arm-send='cd ~/robot-arm-control/ros2_ws && source /opt/ros/humble/setup.bash && source install/setup.bash && ros2 run robot_arm_bringup send_joint_target'
alias arm-status='cd ~/robot-arm-control/ros2_ws && source /opt/ros/humble/setup.bash && export ROBOT_ARM_REPO=~/robot-arm-control && source install/setup.bash && ros2 run robot_arm_bringup arm_status --device /dev/ttyUSB0'
alias arm-torque='cd ~/robot-arm-control/ros2_ws && source /opt/ros/humble/setup.bash && export ROBOT_ARM_REPO=~/robot-arm-control && source install/setup.bash && ros2 run robot_arm_bringup arm_torque --device /dev/ttyUSB0'
alias arm-save-pose='cd ~/robot-arm-control/ros2_ws && source /opt/ros/humble/setup.bash && export ROBOT_ARM_REPO=~/robot-arm-control && source install/setup.bash && ros2 run robot_arm_bringup arm_save_pose --device /dev/ttyUSB0'
```

사용법:

```bash
ls /dev/ttyUSB*
arm-setup
arm-real
arm-send 150 150 155 150 150 150
arm-send 150 150 150 150 150 150
arm-status
arm-torque off
arm-save-pose idle_01_a
arm-torque on
```

주의:

- `arm-setup`은 `git pull`, ROS2 환경 적용, `colcon build`, workspace source까지 한 번에 수행한다.
- `arm-real`은 계속 켜두는 실제 모터 제어 listener다.
- `arm-send`는 반드시 뒤에 J0~J5 각도 6개를 넣어야 한다.
- 예: `arm-send 150 150 155 150 150 150`
- `arm-status`는 J0~J5의 현재 각도, 전압, 온도를 읽는다.
- `arm-torque off`는 홈 자세로 이동한 뒤 토크를 끈다.
- `arm-save-pose 이름`은 현재 J0~J5 각도를 `poses/이름.json`에 저장한다.
- 손으로 티칭 자세를 만들 때만 토크를 끄고, 팔이 갑자기 처지지 않게 받친다.
- 포트가 `/dev/ttyUSB1` 등으로 바뀌면 alias의 `device:=...`를 수정한다.

## 안전 주의

- J1은 가장 큰 부하를 받는 축이다.
- J1은 과부하 보호가 한 번 발생했고, 전원 재인가 후 회복했다.
- 앞으로 뻗는 자세를 오래 유지하지 말 것.
- 처음 테스트는 작은 각도 변화로 시작한다.
- 예: `arm-send 150 150 155 150 150 150`
- 실험 중 모터가 뜨거워지면 중단하고 식힌다.
- 이상 동작 시 홈 복귀 후 전원을 차단한다.

초기 안전 제한은 `kinematics/joint_config.py`에 있다.

## 오늘까지 성공한 것

- 좌표계와 정방향 기구학 기준 정리
- 실측 기반 계산기 작성
- 캘리브레이션 데이터 기록
- GitHub 레포 생성 및 push
- AX-12A Protocol 1.0 드라이버 뼈대 작성
- Jetson에 ROS2 Humble ros-base 설치
- ROS2 topic publish/listen 성공
- ROS2 명령으로 실제 AX-12A 이동 성공
- `arm-real`, `arm-send` 방식으로 제어 흐름 단순화

## 다음 구현 방향

다음 우선순위:

1. Raspberry Pi를 같은 Wi-Fi의 가벼운 HTTP 모터 서버로 만들기
2. Jetson ROS2 노드가 Raspberry Pi HTTP 서버로 목표각 전송
3. AX-12A 온도/전압/현재 위치 읽기 추가
4. J1 과부하 보호 로직 추가
5. 역기구학 구현
6. URDF/MoveIt으로 확장

Raspberry Pi 3는 성능이 약하므로, 처음에는 ROS2를 올리지 않고 Python HTTP 서버로 쓰는 방향을 선호한다.
