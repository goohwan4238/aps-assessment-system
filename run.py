from app import app
import socket

if __name__ == '__main__':
    print("APS 준비도 진단 시스템을 시작합니다...")
    print("로컬 네트워크에서 접속 가능한 주소:")
    print("- http://localhost:5000")
    print("- http://127.0.0.1:5000")
    
    # 로컬 IP 주소 확인
    try:
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        print(f"- http://{local_ip}:5000")
    except:
        print("- 로컬 IP 주소를 확인할 수 없습니다.")
    
    app.run(debug=True, host='0.0.0.0', port=5000)