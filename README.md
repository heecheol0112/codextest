# codextest

터리(햄스터) 다마고치 & 테트리스 샘플

## 빠른 실행 (로컬)
```bash
pip install -r requirements-local.txt
python hamtchi.py        # pygame GUI 다마고치
python tetris.py         # pygame 테트리스
```

## 웹 공유용 (Streamlit)
```bash
pip install -r requirements.txt
streamlit run hamtchi_streamlit.py
```
Streamlit Community Cloud에 이 파일을 올려 배포하면 URL로 공유할 수 있습니다.

> Cloud 빌드 최소화를 위해 `requirements.txt`에는 Streamlit/Pillow만 포함했습니다.  
> 로컬에서 pygame까지 설치하려면 `requirements-local.txt`를 사용하세요.
