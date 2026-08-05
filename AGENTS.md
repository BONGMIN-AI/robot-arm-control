# AGENTS.md

이 파일은 Codex 세션 시작 시 먼저 읽어야 하는 프로젝트 메모다.

## 세션 시작 규칙

새 Codex 세션에서 이 프로젝트를 다룰 때는 먼저 이 파일을 읽고, 이어서 다음 진행 지도를 읽는다.

```text
docs/roadmap.md
```

진행 중 새로 결정된 환경/명령/주의사항은 `AGENTS.md`에, 앞으로의 작업 순서와 체크리스트는 `docs/roadmap.md`에 갱신한다.

## 협업 규칙

- 사용자가 물어본 내용과 관련해 코드를 수정하기 전에는 먼저 수정 의도와 범위를 사용자에게 확인한다.
- 하드웨어 각도, 안전 범위, 속도, 지연 시간, 동작 이름처럼 실제 장치 상태에 의존하는 값은 추측하지 않는다.
- 정보가 부족하면 임의로 정하지 말고 사용자에게 물어본 뒤 진행한다.
- 사용자가 명시한 값이 있으면 그 값을 기준으로 삼고, 임의 기본값으로 덮어쓰지 않는다.

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

저장 포즈 확인/이동:

```bash
arm_list_poses
arm_go_pose sleep_01 --device /dev/ttyUSB0
arm_go_pose sleep_01 --device /dev/ttyUSB0 --allow-unsafe
arm_go_pose sleep_01 --device /dev/ttyUSB0 --allow-unsafe --step 1.0 --delay 0.03 --speed 80
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
echo "alias arm-list-poses='cd ~/robot-arm-control/ros2_ws && source /opt/ros/humble/setup.bash && export ROBOT_ARM_REPO=~/robot-arm-control && source install/setup.bash && ros2 run robot_arm_bringup arm_list_poses'" >> ~/.bashrc
echo "alias arm-go-pose='cd ~/robot-arm-control/ros2_ws && source /opt/ros/humble/setup.bash && export ROBOT_ARM_REPO=~/robot-arm-control && source install/setup.bash && ros2 run robot_arm_bringup arm_go_pose --device /dev/ttyUSB0'" >> ~/.bashrc
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
type arm-list-poses
type arm-go-pose
```

현재 alias 내용만 임시로 다시 잡고 싶으면:

```bash
alias arm-setup='cd ~/robot-arm-control && git pull && cd ros2_ws && source /opt/ros/humble/setup.bash && export ROBOT_ARM_REPO=~/robot-arm-control && colcon build && source install/setup.bash'
alias arm-real='cd ~/robot-arm-control/ros2_ws && source /opt/ros/humble/setup.bash && export ROBOT_ARM_REPO=~/robot-arm-control && source install/setup.bash && ros2 run robot_arm_bringup joint_command_listener --ros-args -p mock:=false -p device:=/dev/ttyUSB0 -p step_deg:=1.0 -p delay_sec:=0.08 -p speed:=50'
alias arm-send='cd ~/robot-arm-control/ros2_ws && source /opt/ros/humble/setup.bash && source install/setup.bash && ros2 run robot_arm_bringup send_joint_target'
alias arm-status='cd ~/robot-arm-control/ros2_ws && source /opt/ros/humble/setup.bash && export ROBOT_ARM_REPO=~/robot-arm-control && source install/setup.bash && ros2 run robot_arm_bringup arm_status --device /dev/ttyUSB0'
alias arm-torque='cd ~/robot-arm-control/ros2_ws && source /opt/ros/humble/setup.bash && export ROBOT_ARM_REPO=~/robot-arm-control && source install/setup.bash && ros2 run robot_arm_bringup arm_torque --device /dev/ttyUSB0'
alias arm-save-pose='cd ~/robot-arm-control/ros2_ws && source /opt/ros/humble/setup.bash && export ROBOT_ARM_REPO=~/robot-arm-control && source install/setup.bash && ros2 run robot_arm_bringup arm_save_pose --device /dev/ttyUSB0'
alias arm-list-poses='cd ~/robot-arm-control/ros2_ws && source /opt/ros/humble/setup.bash && export ROBOT_ARM_REPO=~/robot-arm-control && source install/setup.bash && ros2 run robot_arm_bringup arm_list_poses'
alias arm-go-pose='cd ~/robot-arm-control/ros2_ws && source /opt/ros/humble/setup.bash && export ROBOT_ARM_REPO=~/robot-arm-control && source install/setup.bash && ros2 run robot_arm_bringup arm_go_pose --device /dev/ttyUSB0'
```

오늘 만든 alias 전체 블록:

```bash
alias arm-setup='cd ~/robot-arm-control && git pull && cd ros2_ws && source /opt/ros/humble/setup.bash && export ROBOT_ARM_REPO=~/robot-arm-control && colcon build && source install/setup.bash'
alias arm-real='cd ~/robot-arm-control/ros2_ws && source /opt/ros/humble/setup.bash && export ROBOT_ARM_REPO=~/robot-arm-control && source install/setup.bash && ros2 run robot_arm_bringup joint_command_listener --ros-args -p mock:=false -p device:=/dev/ttyUSB0 -p step_deg:=1.0 -p delay_sec:=0.08 -p speed:=50'
alias arm-send='cd ~/robot-arm-control/ros2_ws && source /opt/ros/humble/setup.bash && source install/setup.bash && ros2 run robot_arm_bringup send_joint_target'
alias arm-status='cd ~/robot-arm-control/ros2_ws && source /opt/ros/humble/setup.bash && export ROBOT_ARM_REPO=~/robot-arm-control && source install/setup.bash && ros2 run robot_arm_bringup arm_status --device /dev/ttyUSB0'
alias arm-torque='cd ~/robot-arm-control/ros2_ws && source /opt/ros/humble/setup.bash && export ROBOT_ARM_REPO=~/robot-arm-control && source install/setup.bash && ros2 run robot_arm_bringup arm_torque --device /dev/ttyUSB0'
alias arm-save-pose='cd ~/robot-arm-control/ros2_ws && source /opt/ros/humble/setup.bash && export ROBOT_ARM_REPO=~/robot-arm-control && source install/setup.bash && ros2 run robot_arm_bringup arm_save_pose --device /dev/ttyUSB0'
alias arm-list-poses='cd ~/robot-arm-control/ros2_ws && source /opt/ros/humble/setup.bash && export ROBOT_ARM_REPO=~/robot-arm-control && source install/setup.bash && ros2 run robot_arm_bringup arm_list_poses'
alias arm-go-pose='cd ~/robot-arm-control/ros2_ws && source /opt/ros/humble/setup.bash && export ROBOT_ARM_REPO=~/robot-arm-control && source install/setup.bash && ros2 run robot_arm_bringup arm_go_pose --device /dev/ttyUSB0'
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
arm-save-pose sleep_01
arm-torque on
arm-list-poses
arm-go-pose sleep_01
arm-go-pose sleep_01 --allow-unsafe --step 1.0 --delay 0.03 --speed 80
```

주의:

- `arm-setup`은 `git pull`, ROS2 환경 적용, `colcon build`, workspace source까지 한 번에 수행한다.
- `arm-real`은 계속 켜두는 실제 모터 제어 listener다.
- `arm-send`는 반드시 뒤에 J0~J5 각도 6개를 넣어야 한다.
- 예: `arm-send 150 150 155 150 150 150`
- `arm-status`는 J0~J5의 현재 각도, 전압, 온도를 읽는다.
- `arm-torque off`는 홈 자세로 이동한 뒤 토크를 끈다.
- `arm-save-pose 이름`은 현재 J0~J5 각도를 `poses/이름.json`에 저장한다.
- `arm-list-poses`는 저장된 포즈 이름 목록을 보여준다.
- `arm-go-pose 이름`은 현재 자세에서 저장된 포즈로 보간 이동한다.
- `arm-go-pose 이름 --allow-unsafe`는 소프트웨어 관절 제한을 적용하지 않고 저장 각도를 그대로 재생한다.
- `arm-list-plays`는 `arm-play`로 실행할 수 있는 저장 동작 이름 목록을 보여준다.
- `sleep_01` 재생 기본 후보는 `--allow-unsafe --step 1.0 --delay 0.03 --speed 80`이다.
- `arm-record 이름`은 홈 복귀 후 토크를 끄고, 스페이스바를 누른 순간부터 J0~J4 손 티칭 흐름을 `recordings/이름.json`에 저장한다.
- `arm-record-list`는 저장된 녹화 이름 목록을 보여준다.
- `arm-record-delete 이름`은 저장된 녹화 `recordings/이름.json`을 삭제한다.
- 녹화 중 `o`는 gripper open 이벤트, `c`는 gripper close 이벤트, `q`는 녹화 종료다.
- `arm-record-play 이름`은 홈 자세 복귀 후 녹화 시작 각도로 이동하고, 기록 흐름을 재생한 뒤 다시 홈으로 복귀한다.
- `arm-record-play`에서 `o/c` 이벤트는 J5가 목표 각도에 도달할 때까지 확인한 뒤 hold 시간을 기다린다.
- `arm-record-play 이름 --sample-stride 3`은 녹화 샘플 3개 중 1개 정도만 보내 전송 수를 줄인다. 첫 샘플, 이벤트 샘플, 마지막 샘플은 유지한다.
- 손으로 티칭 자세를 만들 때만 토크를 끄고, 팔이 갑자기 처지지 않게 받친다.
- 포트가 `/dev/ttyUSB1` 등으로 바뀌면 alias의 `device:=...`를 수정한다.

그리퍼 재생 기본값은 alias나 환경 변수에서 바꿀 수 있게 둔다.

```bash
export GRIP_OPEN=0
export GRIP_CLOSE=150
export GRIP_HOLD=1.0
export GRIP_TOLERANCE=2.0
```

Jetson에서는 다음 함수 이름을 사용한다.

```bash
arm-record() {
  cd ~/robot-arm-control/ros2_ws && source /opt/ros/humble/setup.bash && export ROBOT_ARM_REPO=~/robot-arm-control && source install/setup.bash && ros2 run robot_arm_bringup arm_record --device "${ARM_DEVICE:-/dev/ttyUSB0}" --step "${ARM_STEP:-1.0}" --delay "${ARM_DELAY:-0.03}" --speed "${ARM_SPEED:-80}" "$@"
}

arm-record-list() {
  cd ~/robot-arm-control/ros2_ws && source /opt/ros/humble/setup.bash && export ROBOT_ARM_REPO=~/robot-arm-control && source install/setup.bash && ros2 run robot_arm_bringup arm_record_list "$@"
}

arm-record-delete() {
  cd ~/robot-arm-control/ros2_ws && source /opt/ros/humble/setup.bash && export ROBOT_ARM_REPO=~/robot-arm-control && source install/setup.bash && ros2 run robot_arm_bringup arm_record_delete "$@"
}

arm-list-plays() {
  cd ~/robot-arm-control/ros2_ws && source /opt/ros/humble/setup.bash && export ROBOT_ARM_REPO=~/robot-arm-control && source install/setup.bash && ros2 run robot_arm_bringup arm_list_plays "$@"
}

arm-record-play() {
  cd ~/robot-arm-control/ros2_ws && source /opt/ros/humble/setup.bash && export ROBOT_ARM_REPO=~/robot-arm-control && source install/setup.bash && ros2 run robot_arm_bringup arm_record_play --device "${ARM_DEVICE:-/dev/ttyUSB0}" --step "${ARM_STEP:-1.0}" --delay "${ARM_DELAY:-0.03}" --speed "${ARM_SPEED:-80}" --grip-open "${GRIP_OPEN:-0}" --grip-close "${GRIP_CLOSE:-150}" --grip-hold "${GRIP_HOLD:-1.0}" --grip-tolerance "${GRIP_TOLERANCE:-2.0}" "$@"
}
```

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
- `arm-status`로 실제 J0~J5 현재 각도/전압/온도 읽기 성공
- `arm-torque off`로 홈 복귀 후 토크 끄기 성공
- `arm-save-pose sleep_01`로 첫 티칭 포즈 저장 성공
- `arm-list-poses`, `arm-go-pose` 구현 및 저장 포즈 재생 흐름 정리
- `sleep_01` 원본 각도 재생에는 `--allow-unsafe`가 필요함을 확인
- `sleep_01` 재생 파라미터 후보를 `step=1.0`, `delay=0.03`, `speed=80`으로 결정

## 다음 구현 방향

### 최신 우선순위 (2026-08-05)

아래 기존 우선순위보다 이 결정이 우선한다.

1. 과열/전압/통신 에러 로그 출력 개선
2. `arm-record` 기반 안전 경계 티칭 가이드와 관절 제한 후보 정리
3. 보유 STL + DH 실측 치수 기반의 최소 URDF/RViz 모델 완성 및 시각 검증
4. NHN Cloud Docker GPU 컨테이너의 Isaac Sim + ROS2 환경 준비
5. 역기구학 구현
6. Raspberry Pi HTTP 모터 서버 분리는 완성품 구조가 안정된 뒤 마지막에 재검토

URDF/RViz 현재 상태:

- `ros2_ws/src/robot_arm_description/`에 xacro, launch, `meshes/printed`, `meshes/vendor`를 구성했다.
- `colcon build`, `source install/setup.bash`는 Jetson에서 완료했다.
- RViz 창/모델의 시각적 검증은 아직 하지 않았다.

다음 우선순위:

1. Raspberry Pi를 같은 Wi-Fi의 가벼운 HTTP 모터 서버로 만들기
2. Jetson ROS2 노드가 Raspberry Pi HTTP 서버로 목표각 전송
3. AX-12A 온도/전압/현재 위치 읽기 추가
4. J1 과부하 보호 로직 추가
5. 역기구학 구현
6. URDF/MoveIt으로 확장

Raspberry Pi 3는 성능이 약하므로, 처음에는 ROS2를 올리지 않고 Python HTTP 서버로 쓰는 방향을 선호한다.
