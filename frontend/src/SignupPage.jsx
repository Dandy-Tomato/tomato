import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import './SignupPage.css';
import { POSITIONS, SKILLS } from './constants';
import AlertModal from './components/AlertModal';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8080';

const SignupPage = () => {
    const navigate = useNavigate();
    const location = useLocation();
    const [step, setStep] = useState(1);
    const [isSocial, setIsSocial] = useState(false);
    const [modal, setModal] = useState({
        isOpen: false,
        type: 'success',
        title: '',
        message: '',
        onConfirm: null
    });

    const showAlert = (type, title, message, onConfirm = null) => {
        setModal({ isOpen: true, type, title, message, onConfirm });
    };

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
    const [companyResults, setCompanyResults] = useState([]);
    const [isCompanyLoading, setIsCompanyLoading] = useState(false);

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

    useEffect(() => {
        if (skillSearch.trim()) {
            const filtered = SKILLS.filter(s =>
                s.name.toLowerCase().includes(skillSearch.toLowerCase()) &&
                !techStack.skills.find(ts => ts.id === s.id)
            );
            setSkillResults(filtered.slice(0, 10));
        } else {
            setSkillResults([]);
        }
    }, [skillSearch, techStack.skills]);

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
        if (!emailAvailable) return showAlert('error', '중복 확인 필요', '이메일 중복 확인이 필요합니다.');
        if (!loginInfo.password || loginInfo.password !== loginInfo.confirmPassword) {
            return showAlert('error', '비밀번호 불일치', '비밀번호가 일치하지 않습니다.');
        }

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
                        showAlert('error', '로그인 오류', '자동 로그인에 실패했습니다. 다시 시도해 주세요.');
                    }
                } catch (loginError) {
                    console.error('Auto login error:', loginError);
                    showAlert('error', '서버 오류', '로그인 처리 중 오류가 발생했습니다.');
                }
            } else {
                const signupResult = await signupResponse.json();
                showAlert('error', '회원가입 실패', signupResult.message || '회원가입에 실패했습니다.');
            }
        } catch (error) {
            console.error('Signup error:', error);
            showAlert('error', '서버 오류', '서버 연결 실패');
        }
    };

    // Step 2 Handlers
    useEffect(() => {
        const fetchCompanies = async () => {
            if (companySearch.trim()) {
                setIsCompanyLoading(true);
                try {
                    console.log("Fetching companies for keyword:", companySearch);
                    const response = await fetch(`${API_BASE_URL}/companies/search/auto-complete?keyword=${encodeURIComponent(companySearch)}`);
                    const result = await response.json();
                    console.log("Company Search API Result:", result);
                    if (response.ok && result.data) {
                        const dataArray = Array.isArray(result.data) ? result.data : (result.data.content || []);
                        const filtered = dataArray.filter(c => !profile.companies.some(pc => pc.id === c.id));
                        setCompanyResults(filtered);
                    } else {
                        console.error("Company search failed:", result);
                        setCompanyResults([]);
                    }
                } catch (error) {
                    console.error("Company search error:", error);
                    setCompanyResults([]);
                } finally {
                    setIsCompanyLoading(false);
                }
            } else {
                setCompanyResults([]);
                setIsCompanyLoading(false);
            }
        };

        const timer = setTimeout(fetchCompanies, 300);
        return () => clearTimeout(timer);
    }, [companySearch, profile.companies]);

    const addCompany = (company) => {
        if (!company) return;
        // Check if the company is already added
        if (profile.companies.some(c => c.id === company.id)) {
            showAlert('info', '이미 추가됨', '이미 추가된 기업입니다.');
            return;
        }
        setProfile(prev => ({
            ...prev,
            companies: [...prev.companies, { id: company.id, name: company.name }]
        }));
        setCompanySearch('');
        setCompanyResults([]);
    };

    const removeCompany = (id) => {
        setProfile(prev => ({ ...prev, companies: prev.companies.filter(c => c.id !== id) }));
    };

    // Step 3 Handlers
    const addSkill = (skill) => {
        setTechStack(prev => ({ ...prev, skills: [...prev.skills, skill] }));
        setSkillSearch('');
    };

    const removeSkill = (id) => {
        setTechStack(prev => ({ ...prev, skills: prev.skills.filter(s => s.id !== id) }));
    };

    const handleFinalSubmit = async () => {
        if (!profile.nickname) return showAlert('error', '닉네임 필수', '닉네임을 입력해 주세요.');

        const body = {
            nickname: profile.nickname,
            githubUsername: profile.githubUsername || null,
            positionId: techStack.positionId ? Number(techStack.positionId) : null,
            companyIds: profile.companies.map(c => Number(c.id)),
            skillIds: techStack.skills.map(s => Number(s.id))
        };

        console.log("Onboarding Request Payload (Final - Spec Match):", body);

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

            if (response.ok) {
                const result = await response.json();
                console.log("Onboarding Response - Result:", result);

                showAlert('success', '가입 완료', '회원가입 및 프로필 설정이 완료되었습니다!', () => navigate('/main'));
                if (profile.nickname) {
                    localStorage.setItem('nickname', profile.nickname);
                }
            } else {
                const result = await response.json();
                console.error("Onboarding failed:", result);
                showAlert('error', '오류 발생', `${result.message || '프로필 설정에 실패했습니다.'} (코드: ${response.status})`);
            }
        } catch (error) {
            console.error('Onboarding submit error:', error);
            showAlert('error', '서버 오류', '서버 오류가 발생했습니다. 다시 시도해 주세요.');
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
                    <div style={{ flex: 1, position: 'relative' }}>
                        <div className="input-wrapper">
                            <input
                                type="text"
                                placeholder="기업명을 입력해주세요."
                                value={companySearch}
                                onChange={(e) => setCompanySearch(e.target.value)}
                            />
                        </div>
                        {(isCompanyLoading || (companySearch.trim() && companyResults.length >= 0)) && companySearch.trim() && (
                            <ul className="search-results" style={{
                                position: 'absolute', top: '100%', left: 0, right: 0,
                                backgroundColor: 'white', border: '2px solid #E57358', borderRadius: '10px',
                                boxShadow: '0 10px 20px rgba(0,0,0,0.15)', zIndex: 999999,
                                maxHeight: '250px', overflowY: 'auto', padding: '0', margin: '5px 0 0 0',
                                listStyle: 'none'
                            }}>
                                {isCompanyLoading ? (
                                    <li style={{ padding: '15px', color: '#999', textAlign: 'center' }}>검색 중...</li>
                                ) : (
                                    <>
                                        {companyResults.length > 0 ? (
                                            companyResults.map(c => (
                                                <li
                                                    key={c.id}
                                                    className="result-item"
                                                    onMouseDown={(e) => {
                                                        e.preventDefault();
                                                        addCompany(c);
                                                    }}
                                                    style={{
                                                        padding: '12px 18px', cursor: 'pointer',
                                                        borderBottom: '1px solid #eee', color: '#333', backgroundColor: '#fff'
                                                    }}
                                                    onMouseOver={(e) => e.currentTarget.style.backgroundColor = '#fff5f5'}
                                                    onMouseOut={(e) => e.currentTarget.style.backgroundColor = '#fff'}
                                                >
                                                    {c.name}
                                                </li>
                                            ))
                                        ) : (
                                            <li style={{ padding: '15px', color: '#999', textAlign: 'center' }}>결과가 없습니다.</li>
                                        )}
                                    </>
                                )}
                            </ul>
                        )}
                    </div>
                    <button className="check-button" onClick={() => {
                        if (companyResults.length > 0) {
                            addCompany(companyResults[0]);
                        } else if (companySearch.trim()) {
                            alert("검색 결과에서 기업을 선택해 주세요.");
                        }
                    }}>추가</button>
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
                    <div className="input-wrapper relative" style={{ flex: 1, position: 'relative' }}>
                        <input
                            type="text"
                            placeholder="기술 스택 검색 (예: Java, React)"
                            value={skillSearch}
                            onChange={(e) => setSkillSearch(e.target.value)}
                            style={{ width: '100%', padding: '12px', border: '2px solid #E57358', borderRadius: '8px' }}
                        />
                        {skillResults.length > 0 && (
                            <ul className="search-results" style={{
                                position: 'absolute', top: '100%', left: 0, right: 0,
                                backgroundColor: 'white', border: '2px solid #E57358', borderRadius: '10px',
                                boxShadow: '0 10px 20px rgba(0,0,0,0.15)', zIndex: 99999,
                                maxHeight: '250px', overflowY: 'auto', padding: '0', margin: '5px 0 0 0',
                                listStyle: 'none'
                            }}>
                                {skillResults.map(s => (
                                    <li
                                        key={s.id}
                                        className="result-item"
                                        onClick={() => {
                                            console.log("Signup Skill selected:", s);
                                            addSkill(s);
                                        }}
                                        style={{
                                            padding: '12px 18px',
                                            cursor: 'pointer',
                                            borderBottom: '1px solid #eee',
                                            color: '#333',
                                            backgroundColor: '#fff'
                                        }}
                                        onMouseOver={(e) => e.target.style.backgroundColor = '#fff5f5'}
                                        onMouseOut={(e) => e.target.style.backgroundColor = '#fff'}
                                    >
                                        {s.name}
                                    </li>
                                ))}
                            </ul>
                        )}
                    </div>
                    <button
                        className="check-button"
                        onClick={() => {
                            if (skillResults.length > 0) {
                                addSkill(skillResults[0]);
                            } else {
                                showAlert('info', '검색 결과 없음', '검색 결과가 없습니다. 목록에서 선택해 주세요.');
                            }
                        }}
                    >추가</button>
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

export default SignupPage;
