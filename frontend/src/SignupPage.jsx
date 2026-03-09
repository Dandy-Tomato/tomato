import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import './SignupPage.css';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8080';

// Positions Mapping
const POSITIONS = [
    { id: 1, name: 'Frontend', icon: '💻' },
    { id: 2, name: 'Backend', icon: '🗄️' },
    { id: 3, name: 'Data/AI', icon: '🧠' },
    { id: 4, name: 'Mobile', icon: '📱' },
    { id: 5, name: 'Infra', icon: '☁️' },
    { id: 6, name: 'Embedded', icon: '🔧' },
    { id: 7, name: 'Product', icon: '📦' },
];

// Skills Mapping
const SKILLS = [
    { id: 1, name: 'React' }, { id: 2, name: 'Next.js' }, { id: 3, name: 'Vue.js' }, { id: 4, name: 'Nuxt.js' },
    { id: 5, name: 'Angular' }, { id: 6, name: 'Svelte' }, { id: 7, name: 'TypeScript' }, { id: 8, name: 'JavaScript' },
    { id: 9, name: 'Tailwind CSS' }, { id: 10, name: 'React Native' }, { id: 11, name: 'Flutter' }, { id: 12, name: 'Swift' },
    { id: 13, name: 'Kotlin' }, { id: 14, name: 'Node.js' }, { id: 15, name: 'Spring Boot' }, { id: 16, name: 'Django' },
    { id: 17, name: 'FastAPI' }, { id: 18, name: 'Flask' }, { id: 19, name: 'NestJS' }, { id: 20, name: 'Express.js' },
    { id: 21, name: 'Java' }, { id: 22, name: 'Python' }, { id: 23, name: 'Go' }, { id: 24, name: 'Rust' },
    { id: 25, name: 'C#' }, { id: 26, name: 'PHP' }, { id: 27, name: 'Ruby on Rails' }, { id: 28, name: 'MySQL' },
    { id: 29, name: 'PostgreSQL' }, { id: 30, name: 'MongoDB' }, { id: 31, name: 'Redis' }, { id: 32, name: 'Elasticsearch' },
    { id: 33, name: 'Firebase' }, { id: 34, name: 'Supabase' }, { id: 35, name: 'GraphQL' }, { id: 36, name: 'REST API' },
    { id: 37, name: 'gRPC' }, { id: 38, name: 'Docker' }, { id: 39, name: 'Kubernetes' }, { id: 40, name: 'AWS' },
    { id: 41, name: 'GCP' }, { id: 42, name: 'Azure' }, { id: 43, name: 'GitHub Actions' }, { id: 44, name: 'Jenkins' },
    { id: 45, name: 'Terraform' }, { id: 46, name: 'Nginx' }, { id: 47, name: 'Kafka' }, { id: 48, name: 'RabbitMQ' },
    { id: 49, name: 'WebSocket' }, { id: 50, name: 'OAuth2' }, { id: 51, name: 'JWT' }, { id: 52, name: 'TensorFlow' },
    { id: 53, name: 'PyTorch' }, { id: 54, name: 'LangChain' }, { id: 55, name: 'OpenAI API' }, { id: 56, name: 'Pandas' },
    { id: 57, name: 'Spark' }, { id: 58, name: 'Airflow' }, { id: 59, name: 'Prometheus' }, { id: 60, name: 'Grafana' },
    { id: 61, name: 'C/C++' }, { id: 62, name: 'RTOS' }, { id: 63, name: 'Arduino' }, { id: 64, name: 'Raspberry Pi' },
    { id: 65, name: 'MQTT' }
];

// Dummy Dynamic Company List
const DUMMY_COMPANIES = [
    { id: 1, name: '삼성' }, { id: 2, name: '네이버' }, { id: 3, name: '카카오' },
    { id: 4, name: '라인' }, { id: 5, name: '쿠팡' }, { id: 6, name: '배달의민족' },
    { id: 7, name: '당근' }, { id: 8, name: '토스' }, { id: 9, name: '구글' }
];

const SignupPage = () => {
    const navigate = useNavigate();
    const location = useLocation();
    const [step, setStep] = useState(1);
    const [isSocial, setIsSocial] = useState(false);

    // Step 1 State
    const [loginInfo, setLoginInfo] = useState({
        email: '',
        password: '',
        confirmPassword: ''
    });
    const [showPassword, setShowPassword] = useState(false);
    const [showConfirmPassword, setShowConfirmPassword] = useState(false);
    const [emailAvailable, setEmailAvailable] = useState(null);
    const [emailError, setEmailError] = useState('');

    // Step 2 State (Profile)
    const [profile, setProfile] = useState({
        nickname: '',
        githubUsername: '',
        companies: [] // {id, name}
    });
    const [companySearch, setCompanySearch] = useState('');

    // Step 3 State (Tech Stack)
    const [techStack, setTechStack] = useState({
        positionId: null,
        skills: [] // {id, name}
    });
    const [skillSearch, setSkillSearch] = useState('');
    const [skillResults, setSkillResults] = useState([]);

    useEffect(() => {
        const params = new URLSearchParams(location.search);
        if (params.get('isSocial') === 'true') {
            setIsSocial(true);
            setStep(2); // Social login starts at step 2
        }
    }, [location]);

    const handleLoginInputChange = (e) => {
        const { name, value } = e.target;
        setLoginInfo(prev => ({ ...prev, [name]: value }));
        if (name === 'email') {
            setEmailAvailable(null);
            setEmailError('');
        }
    };

    const checkEmailAvailability = async () => {
        if (!loginInfo.email) {
            setEmailError('이메일을 입력해 주세요.');
            return;
        }
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(loginInfo.email)) {
            setEmailError('올바른 이메일 형식이 아닙니다.');
            return;
        }

        try {
            const response = await fetch(`${API_BASE_URL}/auth/check-email?email=${encodeURIComponent(loginInfo.email)}`);
            const result = await response.json();
            if (response.ok && result.data) {
                setEmailAvailable(result.data.available);
                if (!result.data.available) setEmailError('이미 사용 중인 이메일입니다.');
            } else {
                setEmailError(result.message || '이메일 중복 확인에 실패했습니다.');
            }
        } catch (error) {
            setEmailError('서버 연결에 실패했습니다.');
        }
    };

    const handleSignupStep1 = async () => {
        if (!emailAvailable) return alert('이메일 중복 확인이 필요합니다.');
        if (!loginInfo.password || loginInfo.password !== loginInfo.confirmPassword) return alert('비밀번호가 일치하지 않습니다.');

        try {
            // 1. 회원가입 요청
            const signupResponse = await fetch(`${API_BASE_URL}/auth/signup`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email: loginInfo.email, password: loginInfo.password })
            });

            if (signupResponse.ok) {
                // 2. 가입 성공 시 자동 로그인하여 토큰 획득
                try {
                    const loginResponse = await fetch(`${API_BASE_URL}/auth/login`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ email: loginInfo.email, password: loginInfo.password })
                    });
                    const loginResult = await loginResponse.json();

                    if (loginResponse.ok && loginResult.data) {
                        localStorage.setItem("accessToken", loginResult.data.accessToken);
                        localStorage.setItem("refreshToken", loginResult.data.refreshToken);
                        setStep(2);
                    } else {
                        alert('자동 로그인에 실패했습니다. 다시 시도해 주세요.');
                    }
                } catch (loginError) {
                    console.error('Auto login error:', loginError);
                    alert('로그인 처리 중 오류가 발생했습니다.');
                }
            } else {
                const signupResult = await signupResponse.json();
                alert(signupResult.message || '회원가입에 실패했습니다.');
            }
        } catch (error) {
            console.error('Signup error:', error);
            alert('서버 연결 실패');
        }
    };

    // Step 2 Handlers
    const addCompany = () => {
        if (!companySearch) return;
        const found = DUMMY_COMPANIES.find(c => c.name === companySearch);
        if (found && !profile.companies.some(c => c.id === found.id)) {
            setProfile(prev => ({ ...prev, companies: [...prev.companies, found] }));
            setCompanySearch('');
        } else if (!found) {
            alert('검색된 기능이 없습니다. (현재 데모 데이터: 삼성, 네이버, 카카오 등)');
        }
    };

    const removeCompany = (id) => {
        setProfile(prev => ({ ...prev, companies: prev.companies.filter(c => c.id !== id) }));
    };

    // Step 3 Handlers
    useEffect(() => {
        if (skillSearch) {
            const results = SKILLS.filter(s =>
                s.name.toLowerCase().includes(skillSearch.toLowerCase()) &&
                !techStack.skills.some(ts => ts.id === s.id)
            ).slice(0, 5);
            setSkillResults(results);
        } else {
            setSkillResults([]);
        }
    }, [skillSearch, techStack.skills]);

    const addSkill = (skill) => {
        setTechStack(prev => ({ ...prev, skills: [...prev.skills, skill] }));
        setSkillSearch('');
    };

    const removeSkill = (id) => {
        setTechStack(prev => ({ ...prev, skills: prev.skills.filter(s => s.id !== id) }));
    };

    const handleFinalSubmit = async () => {
        if (!profile.nickname) return alert('닉네임을 입력해 주세요.');

        const body = {
            nickname: profile.nickname,
            githubUsername: profile.githubUsername || null,
            positionId: techStack.positionId || null,
            companyIds: profile.companies.map(c => c.id),
            skillIds: techStack.skills.map(s => s.id)
        };

        const token = localStorage.getItem("accessToken");
        console.log("Onboarding Request - URL:", `${API_BASE_URL}/auth/onboarding`);
        console.log("Onboarding Request - Body:", body);
        console.log("Onboarding Request - Token:", token ? "Exists" : "Missing");

        try {
            const response = await fetch(`${API_BASE_URL}/auth/onboarding`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify(body)
            });

            const result = await response.json();
            console.log("Onboarding Response - Status:", response.status);
            console.log("Onboarding Response - Result:", result);

            if (response.ok) {
                alert('서비스 가입이 모두 완료되었습니다!');
                navigate('/main');
            } else {
                alert(result.message || '온보딩 정보 등록에 실패했습니다.');
            }
        } catch (error) {
            console.error('Onboarding submit error:', error);
            alert('서버 연결 실패 또는 요청 처리 중 오류가 발생했습니다.');
        }
    };

    const renderStep1 = () => (
        <div className="signup-form-content">
            <div className="signup-form-group">
                <label>이메일<span className="required-star">*</span></label>
                <div className="input-with-button">
                    <div className={`input-wrapper ${emailError ? 'input-error' : emailAvailable ? 'input-success' : ''}`}>
                        <svg className="input-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                            <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"></path>
                            <polyline points="22,6 12,13 2,6"></polyline>
                        </svg>
                        <input type="email" name="email" placeholder="이메일을 입력하세요." value={loginInfo.email} onChange={handleLoginInputChange} />
                    </div>
                    <button className="check-button" onClick={checkEmailAvailability}>중복 확인</button>
                </div>
                {emailError && <p className="error-message">{emailError}</p>}
                {emailAvailable && <p className="success-message">사용 가능한 이메일입니다.</p>}
            </div>
            <div className="signup-form-group">
                <label>비밀번호<span className="required-star">*</span></label>
                <div className="input-wrapper">
                    <svg className="input-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect><path d="M7 11V7a5 5 0 0 1 10 0v4"></path></svg>
                    <input type={showPassword ? "text" : "password"} name="password" placeholder="비밀번호를 입력하세요." value={loginInfo.password} onChange={handleLoginInputChange} />
                    <svg className="input-icon-clickable" onClick={() => setShowPassword(!showPassword)} width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">{showPassword ? (<><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path><circle cx="12" cy="12" r="3"></circle></>) : (<><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"></path><line x1="1" y1="1" x2="23" y2="23"></line></>)}</svg>
                </div>
            </div>
            <div className="signup-form-group">
                <label>비밀번호 확인<span className="required-star">*</span></label>
                <div className="input-wrapper">
                    <svg className="input-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect><path d="M7 11V7a5 5 0 0 1 10 0v4"></path></svg>
                    <input type={showConfirmPassword ? "text" : "password"} name="confirmPassword" placeholder="비밀번호를 다시 입력하세요." value={loginInfo.confirmPassword} onChange={handleLoginInputChange} />
                    <svg className="input-icon-clickable" onClick={() => setShowConfirmPassword(!showConfirmPassword)} width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">{showConfirmPassword ? (<><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path><circle cx="12" cy="12" r="3"></circle></>) : (<><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"></path><line x1="1" y1="1" x2="23" y2="23"></line></>)}</svg>
                </div>
            </div>
            <button className="next-button" onClick={handleSignupStep1}>다음</button>
        </div>
    );

    const renderStep2 = () => (
        <div className="signup-form-content">
            <div className="signup-form-group">
                <label>닉네임<span className="required-star">*</span></label>
                <div className="input-wrapper">
                    <input type="text" placeholder="닉네임을 입력하세요." value={profile.nickname} onChange={(e) => setProfile({ ...profile, nickname: e.target.value })} />
                </div>
            </div>
            <div className="signup-form-group">
                <label>취업을 희망하는 기업을 추가해주세요.</label>
                <div className="input-with-button">
                    <div className="input-wrapper">
                        <input type="text" placeholder="기업명을 입력해주세요." value={companySearch} onChange={(e) => setCompanySearch(e.target.value)} />
                    </div>
                    <button className="check-button" onClick={addCompany}>검색</button>
                </div>
                <div className="tag-container">
                    {profile.companies.map(c => (
                        <div key={c.id} className="tag-item">
                            {c.name} <span className="tag-close" onClick={() => removeCompany(c.id)}>✕</span>
                        </div>
                    ))}
                </div>
            </div>
            <div className="signup-form-group">
                <label>GitHub 계정을 추가해주세요.</label>
                <div className="input-wrapper">
                    <input type="text" placeholder="github.com/username" value={profile.githubUsername} onChange={(e) => setProfile({ ...profile, githubUsername: e.target.value })} />
                </div>
            </div>
            <button className="next-button" onClick={() => setStep(3)}>다음</button>
        </div>
    );

    const renderStep3 = () => (
        <div className="signup-form-content">
            <div className="signup-form-group">
                <label>직무를 선택해주세요. (1개만 선택 가능)</label>
                <div className="position-grid">
                    {POSITIONS.map(p => (
                        <button key={p.id} className={`position-item ${techStack.positionId === p.id ? 'active' : ''}`} onClick={() => setTechStack({ ...techStack, positionId: p.id })}>
                            <span className="position-icon">{p.icon}</span>
                            <span className="position-name">{p.name}</span>
                        </button>
                    ))}
                </div>
            </div>
            <div className="signup-form-group">
                <label>보유한 기술 스택을 선택해주세요.</label>
                <div className="input-with-button">
                    <div className="input-wrapper relative">
                        <input type="text" placeholder="검색어를 입력하세요." value={skillSearch} onChange={(e) => setSkillSearch(e.target.value)} />
                        {skillResults.length > 0 && (
                            <div className="search-results">
                                {skillResults.map(s => <div key={s.id} className="result-item" onClick={() => addSkill(s)}>{s.name}</div>)}
                            </div>
                        )}
                    </div>
                    <button className="check-button">검색</button>
                </div>
                <div className="tag-container">
                    {techStack.skills.map(s => (
                        <div key={s.id} className="tag-item">
                            {s.name} <span className="tag-close" onClick={() => removeSkill(s.id)}>✕</span>
                        </div>
                    ))}
                </div>
            </div>
            <button className="next-button" onClick={handleFinalSubmit}>완료</button>
        </div>
    );

    return (
        <div className="signup-page-wrapper">
            <div className="signup-card">
                <h1 className="signup-title">회원가입</h1>
                <p className="signup-subtitle">TOMATO와 함께 프로젝트를 시작해보세요.</p>
                <div className="stepper-container">
                    <div className={`step-item ${step >= 1 ? 'active' : ''}`}>
                        <div className="step-circle">1</div>
                        <span className="step-label">로그인 정보</span>
                    </div>
                    <div className="step-line"></div>
                    <div className={`step-item ${step >= 2 ? 'active' : ''}`}>
                        <div className="step-circle">2</div>
                        <span className="step-label">프로필 설정</span>
                    </div>
                    <div className="step-line"></div>
                    <div className={`step-item ${step >= 3 ? 'active' : ''}`}>
                        <div className="step-circle">3</div>
                        <span className="step-label">기술 스택</span>
                    </div>
                </div>
                {step === 1 && renderStep1()}
                {step === 2 && renderStep2()}
                {step === 3 && renderStep3()}
            </div>
        </div>
    );
};

export default SignupPage;
