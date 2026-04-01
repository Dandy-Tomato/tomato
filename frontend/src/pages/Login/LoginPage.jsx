import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './LoginPage.css';

// 상위 에셋과 공통 모달 경로로 수정
import tomatoImg from '../../assets/tomato_character.png';
import AlertModal from '../../components/common/AlertModal';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8080';

/**
 * 로그인 페이지 뷰 컴포넌트
 * 일반적인 아이디/비밀번호 기반 폼 로그인과 소셜 로그인(구글, 깃허브)을 제공합니다.
 */
const LoginPage = () => {
    const navigate = useNavigate();
    
    // 비밀번호 가리기/보여주기 토글 상태
    const [showPassword, setShowPassword] = useState(false);
    
    // 사용자가 입력한 로그인 폼 데이터
    const [loginInfo, setLoginInfo] = useState({
        email: '',
        password: ''
    });
    
    // 알림창(모달) 상태 관리
    const [modal, setModal] = useState({
        isOpen: false,
        type: 'success',
        title: '',
        message: '',
        onConfirm: null
    });

    /**
     * 알림창 모달 노출 처리 헬퍼 함수
     */
    const showAlert = (type, title, message, onConfirm = null) => {
        setModal({ isOpen: true, type, title, message, onConfirm });
    };

    /**
     * 비밀번호 노출 토글 핸들러
     */
    const togglePasswordVisibility = () => {
        setShowPassword(!showPassword);
    };

    /**
     * input 변경 이벤트 시 호출되어 상태에 데이터를 반영하는 함수입니다.
     */
    const handleInputChange = (e) => {
        const { name, value } = e.target;
        setLoginInfo(prev => ({
            ...prev,
            [name]: value
        }));
    };

    /**
     * 일반 이메일-비밀번호 방식의 로그인 처리 함수입니다.
     */
    const handleLogin = async () => {
        if (!loginInfo.email || !loginInfo.password) {
            showAlert('error', '입력 오류', '이메일과 비밀번호를 모두 입력해 주세요.');
            return;
        }

        try {
            // API 서버에 로그인 정보 데이터 전송
            const response = await fetch(`${API_BASE_URL}/auth/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    email: loginInfo.email,
                    password: loginInfo.password
                }),
            });

            const result = await response.json();

            if (response.ok && result.data) {
                // 검증 성공 확인 및 발급받은 JWT 관련 정보를 로컬 스토리지에 저장합니다.
                localStorage.setItem("accessToken", result.data.accessToken);
                localStorage.setItem("refreshToken", result.data.refreshToken);
                localStorage.setItem("userId", result.data.userId); // userId 정보 저장

                // 성공 메시지 모달이 뜨고 '확인' 클릭 시 메인 페이지로 이동합니다.
                showAlert('success', '로그인 성공', '토마토에 오신 것을 환영합니다!', () => navigate('/main', { replace: true }));
            } else {
                // 에러 처리: 서버에서 내려준 오류 메시지를 출력합니다. (400, 401 등)
                showAlert('error', '로그인 실패', result.message || '로그인에 실패했습니다. 정보를 확인해 주세요.');
            }
        } catch (error) {
            console.error('Login error:', error);
            showAlert('error', '서버 오류', '서버 연결에 실패했습니다. 잠시 후 다시 시도해 주세요.');
        }
    };

    /**
     * OAuth 기반의 소셜 로그인 이동용 핸들러 (구글, 깃허브 지원 기능 연동용)
     * 실제 프로세스는 백엔드 쪽에서 담당하므로, 해당 인증 엔드포인트 URL로 리다이렉트 시킵니다.
     * @param {string} provider - 'google' | 'github'
     */
    const handleSocialLogin = (provider) => {
        window.location.href = `${API_BASE_URL}/oauth2/authorization/${provider}`;
    };

    return (
        <div className="login-card-wrapper">
            <div className="login-card">
                {/* 좌측 패널: 토마토 브랜드 심볼 및 캐치프레이즈 출력 영역 */}
                <div className="login-left">
                    <div className="branding-container">
                        <img src={tomatoImg} alt="Tomato Character" className="character-img" />
                        <h1 className="brand-title">TOMATO</h1>
                        <p className="brand-subtitle">Stop guessing. Start building</p>
                    </div>
                </div>

                {/* 우측 패널: 실제 로그인을 수행하는 입력 영역 폼 */}
                <div className="login-right">
                    <div className="form-container">
                        <h2 className="welcome-title">오셨군요!</h2>
                        <p className="welcome-subtitle">계속하려면 정보를 입력해주세요.</p>

                        {/* 이메일 주소 입력란 */}
                        <div className="form-group">
                            <label>이메일 주소</label>
                            <div className="input-wrapper">
                                <svg className="input-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                    <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"></path>
                                    <polyline points="22,6 12,13 2,6"></polyline>
                                </svg>
                                <input
                                    type="email"
                                    name="email"
                                    placeholder="tomato@gmail.com"
                                    value={loginInfo.email}
                                    onChange={handleInputChange}
                                />
                            </div>
                        </div>

                        {/* 비밀번호 입력란 */}
                        <div className="form-group">
                            <label>비밀번호</label>
                            <div className="input-wrapper">
                                <svg className="input-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                    <rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect>
                                    <path d="M7 11V7a5 5 0 0 1 10 0v4"></path>
                                </svg>
                                <input
                                    type={showPassword ? "text" : "password"}
                                    name="password"
                                    placeholder="비밀번호를 입력하세요."
                                    value={loginInfo.password}
                                    onChange={handleInputChange}
                                    onKeyPress={(e) => { 
                                        // 편의를 위해 Enter 입력 시 폼 서밋
                                        if (e.key === 'Enter') handleLogin(); 
                                    }}
                                />
                                
                                {/* 비밀번호 보기/숨기기 눈 버튼 아이콘 */}
                                <svg
                                    className="input-icon-clickable"
                                    onClick={togglePasswordVisibility}
                                    width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"
                                >
                                    {showPassword ? (
                                        <>
                                            <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
                                            <circle cx="12" cy="12" r="3"></circle>
                                        </>
                                    ) : (
                                        <>
                                            <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"></path>
                                            <line x1="1" y1="1" x2="23" y2="23"></line>
                                        </>
                                    )}
                                </svg>
                            </div>
                        </div>

                        {/* 메인 로그인 버튼 */}
                        <button className="login-button" onClick={handleLogin}>로그인</button>

                        <div className="divider">
                            <span>또는 다음으로 계속하기</span>
                        </div>

                        {/* 제공되는 소셜 로그인 버튼 */}
                        <div className="social-buttons">
                            {/* 구글 Auth 버튼 */}
                            <button className="google-button" onClick={() => handleSocialLogin('google')}>
                                <svg width="20" height="20" viewBox="0 0 24 24">
                                    <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" />
                                    <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" />
                                    <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l3.66-2.84z" />
                                    <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" />
                                </svg>
                                Google
                            </button>

                            {/* GitHub Auth 버튼 */}
                            <button className="github-button" onClick={() => handleSocialLogin('github')}>
                                <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                                    <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z" />
                                </svg>
                                GitHub
                            </button>
                        </div>

                        {/* 신규 가입 유도 문구 */}
                        <p className="signup-text">
                            아직 계정이 없으신가요? <span className="signup-link" onClick={() => navigate('/signup')}>무료로 시작하기</span>
                        </p>
                    </div>
                </div>
            </div>
            
            <AlertModal 
                isOpen={modal.isOpen}
                type={modal.type}
                title={modal.title}
                message={modal.message}
                onClose={() => {
                    setModal(prev => ({ ...prev, isOpen: false }));
                    if (modal.onConfirm) modal.onConfirm();
                }}
            />
        </div>
    );
};

export default LoginPage;
