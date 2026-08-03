# Robot Arm Roadmap

이 문서는 앞으로 로봇암 프로젝트를 진행할 때 따라가는 지도다.  
새 세션을 시작하면 `AGENTS.md`를 읽고, 이어서 이 파일을 읽은 뒤 현재 단계부터 진행한다.

## 현재 상태

완료:

- AX-12A 6개 모터 ID 정리: `J0=0` ... `J5=5`
- 실측 기반 정방향 기구학 계산기 작성
- 캘리브레이션 1차 완료
- Jetson AGX에 ROS2 Humble `ros-base` 설치
- ROS2 topic publish/listen 테스트 성공
- Jetson에서 `/dev/ttyUSB0` 또는 `/dev/ttyUSB1`로 AX-12A 실제 제어 성공
- `arm-real`, `arm-send`, `arm-setup` alias 흐름 정리 중
- `AGENTS.md`에 프로젝트 환경 기록

현재 주의점:

- J1은 부하가 가장 크고 과부하 보호가 발생한 적 있음
- 처음 테스트는 작은 각도 변화로만 진행
- USB 포트는 매번 바뀔 수 있음: `/dev/ttyUSB0`, `/dev/ttyUSB1` 확인 필요

## 진행 원칙

1. 작은 단위로 구현한다.
2. 실제 모터 실행 전 mock 또는 작은 각도 테스트를 먼저 한다.
3. 작동한 단위는 Git commit으로 남긴다.
4. 새로 알게 된 설정/환경은 `AGENTS.md` 또는 관련 문서에 기록한다.
5. 오늘 할 단계는 이 문서의 체크박스로 갱신한다.

## 전체 진행 순서

현재 성공 지점은 터미널 2개에서 ROS2 노드로 목표 각도를 보내고 실제 AX-12A 제어까지 되는 단계다.  
이후에는 다음 순서를 따른다.

1. 상태 읽기: 현재 각도, 온도, 전압을 읽는 `arm-status` 계열 명령을 만든다.
2. 동작 저장/재생: `motions/*.json`에 포즈 시퀀스를 저장하고 `arm-play`로 실행한다.
3. 티칭 모드: 현재 자세를 `arm-save-pose`로 저장하고 여러 포즈를 동작으로 묶는다.
4. 안전 계층: J1 보호, 온도/전압 감시, 속도/step 제한, 홈 복귀 전략을 넣는다.
5. 목표 위치 제어: 역기구학으로 `x,y,z` 목표를 J0~J3 각도로 변환한다.
6. Raspberry Pi 서버 분리: Pi를 가벼운 HTTP 모터 서버로 만들고 Jetson ROS2가 요청을 보낸다.
7. URDF/RViz: 실측 치수와 joint limit을 모델에 반영하고 실제 관절 방향과 맞춘다.
8. Isaac Sim: URDF를 가져와 저장 동작을 재생한 뒤, 실제 로봇과 차이를 비교한다.
9. 학습 확장: 저장 동작/상태 로그를 바탕으로 모방학습 또는 강화학습을 검토한다.

## Phase 1. Jetson 직접 제어 안정화

목표: Jetson에서 ROS2 명령으로 AX-12A를 안정적으로 움직인다.

체크리스트:

- [x] ROS2 listener 노드 작성
- [x] ROS2 sender 노드 작성
- [x] 실제 AX-12A 이동 성공
- [ ] `arm-setup` alias를 Jetson `~/.bashrc`에 등록
- [ ] `arm-real` alias의 포트를 현재 장치에 맞게 정리
- [ ] 포트 확인 절차를 반복 가능하게 정리
- [ ] J1 과부하 발생 조건 기록
- [ ] 안전 테스트 자세 목록 만들기

기본 실행 순서:

```bash
ls /dev/ttyUSB*
arm-setup
arm-real
arm-send 150 150 155 150 150 150
arm-send 150 150 150 150 150 150
```

성공 기준:

- `arm-real` 실행 후 listener가 정상 대기한다.
- `arm-send`로 J2 또는 J3를 5도 정도 움직일 수 있다.
- 홈 복귀가 정상 작동한다.

## Phase 2. 안전/진단 기능 추가

목표: 모터 상태를 읽고 위험한 움직임을 줄인다.

체크리스트:

- [x] `raspberry_pi/read_status.py` 상태 읽기 명령 추가
- [x] ROS2 패키지에 `arm_status` 콘솔 명령 추가
- [x] 홈 복귀 후 토크를 끄는 `arm_torque off` 명령 추가
- [x] 현재 자세를 `poses/<name>.json`으로 저장하는 `arm_save_pose` 명령 추가
- [x] 저장된 포즈 목록을 보는 `arm_list_poses` 명령 추가
- [x] 저장된 포즈로 이동하는 `arm_go_pose` 명령 추가
- [x] 티칭 포즈 원본 각도 재생용 `arm_go_pose --allow-unsafe` 옵션 추가
- [x] `sleep_01` 재생 파라미터 후보 결정: `--step 1.0 --delay 0.03 --speed 80`
- [x] Jetson에서 실제 장치 `arm-status` 실행 확인
- [x] Jetson에서 `arm-torque off` 안전 동작 확인
- [x] Jetson에서 `arm-save-pose sleep_01` 저장 성공
- [x] AX-12A 현재 위치 읽기 테스트
- [x] AX-12A 온도 읽기 테스트
- [x] AX-12A 전압 읽기 테스트
- [ ] 에러 발생 시 로그를 보기 쉽게 출력
- [ ] J1 과부하 보호 발생 시 홈 복귀/정지 전략 정리
- [x] `arm-status` alias를 Jetson `~/.bashrc`에 등록
- [x] `arm-torque` alias를 Jetson `~/.bashrc`에 등록
- [x] `arm-save-pose` alias를 Jetson `~/.bashrc`에 등록
- [ ] `arm-list-poses` alias를 Jetson `~/.bashrc`에 등록
- [ ] `arm-go-pose` alias를 Jetson `~/.bashrc`에 등록
- [x] 연속 티칭 녹화 명령 `arm-record` 추가
- [x] 저장 녹화 목록 명령 `arm-record-list` 추가
- [x] 녹화 동작 재생 명령 `arm-record-play` 추가
- [x] `arm-record-play` 실행 순서 정리: 홈 복귀 -> 녹화 시작 각도 이동 -> 기록 흐름 재생
- [x] 그리퍼 이벤트 `o=open`, `c=close` 재생 로직 추가

필요 코드 후보:

```text
raspberry_pi/read_status.py              # 추가됨
raspberry_pi/torque_control.py           # 추가됨
raspberry_pi/pose_store.py               # 추가됨
raspberry_pi/list_poses.py               # 추가됨
raspberry_pi/go_pose.py                  # 추가됨
raspberry_pi/list_recordings.py          # 추가됨
raspberry_pi/recording_store.py          # 추가됨
raspberry_pi/record_motion.py            # 추가됨
raspberry_pi/record_play.py              # 추가됨
ros2_ws/src/robot_arm_bringup/robot_arm_bringup/status_publisher.py
```

성공 기준:

- 각 모터의 현재 각도, 전압, 온도를 읽을 수 있다.
- J1이 뜨거워지거나 전압이 낮을 때 바로 확인할 수 있다.
- 손으로 만든 J0~J4 흐름을 `recordings/<name>.json`에 저장할 수 있다.
- 녹화 재생은 어떤 자세에서 시작하든 홈 자세를 거친 뒤 녹화 시작 각도로 이동한다.
- `o/c` 이벤트는 J5가 목표 각도에 도달한 것을 확인하고 `GRIP_HOLD`만큼 기다린 뒤 다음 팔 움직임으로 넘어간다.

## Phase 3. Raspberry Pi 모터 서버

목표: Raspberry Pi를 같은 Wi-Fi에서 가벼운 모터 제어 서버로 사용한다.

권장 구조:

```text
Jetson ROS2
  -> HTTP request
Raspberry Pi Python server
  -> motion_plan
  -> AX-12A
```

체크리스트:

- [ ] Raspberry Pi OS/Ubuntu 상태 확인
- [ ] Raspberry Pi에 Python, git, dynamixel-sdk 설치
- [ ] Raspberry Pi에서 `move_once.py --mock` 실행
- [ ] Raspberry Pi에서 실제 AX-12A 포트 확인
- [ ] `raspberry_pi/server.py` HTTP 서버 구현
- [ ] `GET /health` 구현
- [ ] `POST /move` 구현
- [ ] Jetson에서 `curl`로 Pi 서버 호출
- [ ] ROS2 listener가 직접 모터를 움직이는 대신 Pi 서버로 명령 보내도록 옵션화

성공 기준:

- Jetson에서 HTTP 요청을 보내면 Raspberry Pi가 모터를 움직인다.
- Raspberry Pi에는 ROS2를 올리지 않아도 된다.

## Phase 4. 역기구학

목표: 각도를 직접 넣는 방식에서 목표 위치를 넣는 방식으로 발전한다.

현재:

```text
각도 -> x,y,z
```

목표:

```text
x,y,z -> 각도
```

체크리스트:

- [ ] J0 yaw 계산 분리
- [ ] y-z 평면에서 J1/J2/J3 역기구학 단순 모델 만들기
- [ ] 손목 pitch를 단순 고정하는 버전 구현
- [ ] 목표 위치가 도달 가능한지 검사
- [ ] 역기구학 결과를 `motion_plan`으로 연결
- [ ] 실제 로봇에서 작은 목표 위치 테스트

필요 코드 후보:

```text
kinematics/inverse_kinematics.py
kinematics/reachability.py
```

성공 기준:

- `x=0, y=100, z=480` 같은 목표를 넣으면 안전한 J0~J3 각도가 나온다.

## Phase 5. 모델링: URDF / RViz / MoveIt

목표: 로봇팔 모델을 ROS2 도구에서 시각화하고, 나중에 MoveIt으로 확장한다.

체크리스트:

- [ ] 현재 실측 치수를 URDF/xacro로 옮기기
- [ ] joint limit 반영
- [ ] RViz에서 joint state 움직임 확인
- [ ] Jetson 또는 PC에서 RViz 실행 환경 결정
- [ ] MoveIt Setup Assistant 검토

성공 기준:

- RViz에서 J0~J5를 움직였을 때 실제 로봇과 같은 방향으로 보인다.

## Phase 6. 포트폴리오 정리

목표: 기술적으로 설명 가능한 프로젝트 기록을 만든다.

체크리스트:

- [x] 2026-08-01 포트폴리오 기록 작성
- [x] 2026-08-01 공부 자료 작성
- [ ] GitHub README를 외부 공개용으로 정리
- [ ] 회로/통신 구조 다이어그램 추가
- [ ] 캘리브레이션 사진/표 추가
- [ ] 실제 동작 영상 링크 추가

## 다음 세션에서 바로 할 일

우선순위:

1. Jetson에서 코드 업데이트 후 ROS2 워크스페이스 빌드
2. `arm_status --mock` 실행 확인
3. 실제 포트를 확인한 뒤 `arm_status --device /dev/ttyUSB0` 또는 `/dev/ttyUSB1` 실행
4. 작은 각도 테스트:

```bash
arm-send 150 150 155 150 150 150
arm-send 150 150 150 150 150 150
```

5. `arm-list-poses`, `arm-go-pose` alias 등록
6. `arm-list-poses`에서 `sleep_01` 확인
7. 기본 `arm-go-pose sleep_01`는 안전 제한 때문에 J1/J2/J3가 잘리는지 확인
8. 필요할 때만 `arm-go-pose sleep_01 --allow-unsafe --step 1.0 --delay 0.03 --speed 80`로 저장 원본 각도 재생 테스트
9. 다음 구현: `motions/*.json`에 여러 포즈를 묶고 `arm-play`로 idle 동작 재생

## 결정 보류

- Raspberry Pi OS 선택
- Raspberry Pi에 ROS2를 올릴지, HTTP 서버만 쓸지
- RViz를 Jetson에서 돌릴지 PC에서 돌릴지
- J1 부하 보상을 기계적으로 할지, 제어 제한으로만 갈지
