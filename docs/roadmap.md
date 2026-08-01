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

- [ ] AX-12A 현재 위치 읽기 테스트
- [ ] AX-12A 온도 읽기 테스트
- [ ] AX-12A 전압 읽기 테스트
- [ ] 에러 발생 시 로그를 보기 쉽게 출력
- [ ] J1 과부하 보호 발생 시 홈 복귀/정지 전략 정리
- [ ] `arm-status` 명령 추가 검토

필요 코드 후보:

```text
raspberry_pi/read_status.py
ros2_ws/src/robot_arm_bringup/robot_arm_bringup/status_publisher.py
```

성공 기준:

- 각 모터의 현재 각도, 전압, 온도를 읽을 수 있다.
- J1이 뜨거워지거나 전압이 낮을 때 바로 확인할 수 있다.

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

1. Jetson에서 `arm-setup` alias 등록 확인
2. `arm-real` 포트를 현재 `/dev/ttyUSB0` 기준으로 맞추기
3. 작은 각도 테스트:

```bash
arm-send 150 150 155 150 150 150
arm-send 150 150 150 150 150 150
```

4. AX-12A 상태 읽기 기능 추가 시작

## 결정 보류

- Raspberry Pi OS 선택
- Raspberry Pi에 ROS2를 올릴지, HTTP 서버만 쓸지
- RViz를 Jetson에서 돌릴지 PC에서 돌릴지
- J1 부하 보상을 기계적으로 할지, 제어 제한으로만 갈지

