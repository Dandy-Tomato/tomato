import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import './ProfilePage.css';
import { MdPerson, MdCode, MdBusiness } from 'react-icons/md';
import { POSITIONS, SKILLS } from './constants';
import AlertModal from './components/AlertModal';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8080';

const ProfilePage = () => {
    const [isEditing, setIsEditing] = useState(false);
    const [loading, setLoading] = useState(true);
    const [profile, setProfile] = useState({
        email: '',
        nickname: '',
        githubUsername: '',
        positionId: null,
        skillIds: [],
        companies: [] // {id, name}
    });
    const [skillSearch, setSkillSearch] = useState('');
    const [skillResults, setSkillResults] = useState([]);
    const [companySearch, setCompanySearch] = useState('');
    const [companyResults, setCompanyResults] = useState([]);
    const [isCompanyLoading, setIsCompanyLoading] = useState(false);
    const [modal, setModal] = useState({ isOpen: false, type: 'success', title: '', message: '', onConfirm: null });

    const showAlert = (type, title, message, onConfirm = null) => {
        setModal({ isOpen: true, type, title, message, onConfirm });
    };

    useEffect(() => {
        console.log("Skill search active. Input:", skillSearch, "Total SKILLS:", SKILLS.length);
        if (skillSearch.trim()) {
            const searchTerm = skillSearch.toLowerCase();
            const filtered = SKILLS.filter(s =>
                s.name.toLowerCase().includes(searchTerm) &&
                !profile.skillIds.includes(s.id)
            );
            console.log("Filtered results:", filtered);
            setSkillResults(filtered.slice(0, 10));
        } else {
            setSkillResults([]);
        }
    }, [skillSearch, profile.skillIds]);

    useEffect(() => {
        fetchProfile();
    }, []);

    useEffect(() => {
        const fetchCompanies = async () => {
            if (companySearch.trim()) {
                setIsCompanyLoading(true);
                try {
                    console.log("Profile Fetching companies for keyword:", companySearch);
                    const token = localStorage.getItem("accessToken");
                    const response = await fetch(`${API_BASE_URL}/companies/search/auto-complete?keyword=${encodeURIComponent(companySearch)}`, {
                        headers: token ? { 'Authorization': `Bearer ${token}` } : {}
                    });
                    const result = await response.json();
                    console.log("Company Search API Result (Profile):", result);
                    if (response.ok && result.data) {
                        const dataArray = Array.isArray(result.data) ? result.data : (result.data.content || []);
                        console.log("Profile Processed Data Array:", dataArray);
                        const filtered = dataArray.filter(c => 
                            !profile.companies.some(pc => 
                                (c.id && pc.id === c.id) || (pc.name === c.name)
                            )
                        );
                        setCompanyResults(filtered);
                    } else {
                        console.error("Company search failure (Profile):", result);
                    }
                } catch (error) {
                    console.error("Company search error (Profile):", error);
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

    const fetchProfile = async () => {
        const token = localStorage.getItem("accessToken");
        if (!token) {
            showAlert('error', '로그인 필요', '로그인이 필요합니다.');
            window.location.href = '/';
            return;
        }

        try {
            const response = await fetch(`${API_BASE_URL}/users/profile`, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });
            const result = await response.json();
            console.log("Profile Page API Result:", result);

            if (response.ok && result.data) {
                const data = result.data;

                // 직무 정보 파싱 (새 스펙: position이 정수형 ID로 옴)
                const posId = (data.position !== undefined && data.position !== null) ? Number(data.position) : 
                              (data.positionId || data.job || data.position_id);
                
                // 기업 정보 파싱 (새 스펙: companies: [{id, name}, ...])
                const rawCompanies = data.companies || [];
                const finalCompanies = rawCompanies.map(c => ({
                    id: c.id != null ? Number(c.id) : (c.companyId != null ? Number(c.companyId) : null),
                    name: c.name || c.companyName || `기업 ${c.id || c.companyId}`
                }));

                setProfile({
                    email: data.email || '',
                    nickname: data.nickname || '',
                    githubUsername: data.githubUsername || '',
                    positionId: posId,
                    skillIds: (data.skillIds || []).map(id => Number(id)),
                    companies: finalCompanies
                });
                
                if (data.nickname && data.nickname !== "null") {
                    localStorage.setItem('nickname', data.nickname);
                }
                if (data.user_id || data.userId) {
                    localStorage.setItem('userId', data.user_id || data.userId);
                }
            } else {
                console.error("Failed to fetch profile:", result.message);
            }
        } catch (error) {
            console.error("Error fetching profile:", error);
        } finally {
            setLoading(false);
        }
    };

    const handleEditToggle = () => setIsEditing(!isEditing);

    const handleSave = async () => {
        const token = localStorage.getItem("accessToken");

        const body = {
            nickname: profile.nickname,
            githubUsername: profile.githubUsername || null,
            positionId: profile.positionId ? Number(profile.positionId) : null,
            companyIds: profile.companies
                .map(c => c.id || c.companyId)
                .filter(id => id !== undefined && id !== null && !isNaN(Number(id)))
                .map(id => Number(id)),
            skillIds: profile.skillIds.map(id => Number(id))
        };

        console.log("Profile Save Body (Final - Spec Match):", body);

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
            console.log("Save Response Status:", response.status);
            console.log("Save Response Data:", result);

            if (response.ok) {
                showAlert('success', '저장 완료', '프로필이 수정되었습니다.', () => {
                    setIsEditing(false);
                    fetchProfile();
                });
            } else {
                const errorMsg = result.message || '수정에 실패했습니다.';
                const errorCode = result.errorCode ? ` (에러 코드: ${result.errorCode})` : '';
                showAlert('error', '저장 실패', `${errorMsg}${errorCode}`);
                console.error('Save failure details:', result);
            }
        } catch (error) {
            console.error('Error updating profile:', error);
            showAlert('error', '서버 오류', '서버 오류가 발생했습니다. 네트워크 상태를 확인해 주세요.');
        }
    };

    if (loading) return <div className="loading">로딩 중...</div>;

    // 도움 함수들
    const getPositionName = (id) => POSITIONS.find(p => Number(p.id) === Number(id))?.name || id || '없음';
    const getSkillName = (id) => SKILLS.find(s => Number(s.id) === Number(id))?.name || id;

    const addSkill = (skill) => {
        setProfile(prev => {
            if (prev.skillIds.includes(skill.id)) return prev;
            return { ...prev, skillIds: [...prev.skillIds, skill.id] };
        });
        setSkillSearch('');
    };

    const addCompany = (company) => {
        if (!company) return;
        const cId = company.id || company.companyId;
        const cName = company.name || company.companyName;

        setProfile(prev => {
            const already = prev.companies.some(c =>
                (cId && (c.id === cId || c.companyId === cId)) || (cName && (c.name === cName || c.companyName === cName))
            );
            if (already) return prev;
            return { ...prev, companies: [...prev.companies, { id: cId, name: cName }] };
        });
        setCompanySearch('');
        setCompanyResults([]);
    };

    return (
        <div className="profile-page">
            <Navbar />
            <main className="profile-content">

                {/* 기본 정보 섹션 */}
                <section className="profile-card">
                    <div className="card-header">
                        <h2 className="card-title">기본 정보</h2>
                        <MdPerson className="header-icon" />
                    </div>
                    <div className="info-list">
                        <div className="info-item">
                            <span className="info-label">이메일</span>
                            <span className="info-value">{profile.email}</span>
                        </div>
                        <div className="info-item">
                            <span className="info-label">닉네임</span>
                            {isEditing ? (
                                <input
                                    className="edit-input"
                                    value={profile.nickname}
                                    onChange={(e) => setProfile({ ...profile, nickname: e.target.value })}
                                />
                            ) : (
                                <span className="info-value">{profile.nickname}</span>
                            )}
                        </div>
                        <div className="info-item">
                            <span className="info-label">GitHub</span>
                            {isEditing ? (
                                <input
                                    className="edit-input"
                                    value={profile.githubUsername}
                                    onChange={(e) => setProfile({ ...profile, githubUsername: e.target.value })}
                                    placeholder="github.com/username"
                                />
                            ) : (
                                <span className="info-value link">{profile.githubUsername || '등록된 계정 없음'}</span>
                            )}
                        </div>
                    </div>
                </section>

                {/* 기술 스택 섹션 */}
                <section className="profile-card">
                    <div className="card-header">
                        <h2 className="card-title">기술 스택</h2>
                        <MdCode className="header-icon" />
                    </div>
                    <div className="stack-content">
                        <p className="stack-label">직무</p>
                        <div className="position-tags">
                            {POSITIONS.map(pos => (
                                <button
                                    key={pos.id}
                                    className={`tag-button ${Number(profile.positionId) === Number(pos.id) ? 'active' : ''}`}
                                    disabled={!isEditing}
                                    onClick={() => setProfile({ ...profile, positionId: pos.id })}
                                >
                                    {pos.name}
                                </button>
                            ))}
                        </div>

                        <p className="stack-label">보유 기술 스택</p>
                        <div className="skill-tags">
                            {profile.skillIds.map(id => (
                                <span key={id} className="skill-tag">
                                    {getSkillName(id)}
                                    {isEditing && (
                                        <span
                                            className="tag-remove"
                                            onClick={() => setProfile({ ...profile, skillIds: profile.skillIds.filter(s => s !== id) })}
                                        >✕</span>
                                    )}
                                </span>
                            ))}
                        </div>

                        {isEditing && (
                            <div className="skill-search" style={{ position: 'relative', marginTop: '20px' }}>
                                <p className="stack-label">보유한 기술 스택을 선택해주세요.</p>
                                <div className="search-bar" style={{ position: 'relative', display: 'flex', gap: '10px' }}>
                                    <div className="search-input-wrapper" style={{ position: 'relative', flex: 1 }}>
                                        <input
                                            type="text"
                                            placeholder="기술 스택 검색 (예: Java, React)"
                                            value={skillSearch}
                                            onChange={(e) => setSkillSearch(e.target.value)}
                                            style={{
                                                width: '100%',
                                                padding: '12px',
                                                borderRadius: '8px',
                                                border: '1px solid #ff6b6b',
                                                fontSize: '14px',
                                                boxSizing: 'border-box'
                                            }}
                                        />
                                        {skillResults.length > 0 && (
                                            <ul role="listbox" style={{
                                                position: 'absolute',
                                                top: '100%',
                                                left: 0,
                                                right: 0,
                                                backgroundColor: '#ffffff',
                                                border: '2px solid #ff6b6b',
                                                borderRadius: '8px',
                                                boxShadow: '0 10px 25px rgba(0,0,0,0.2)',
                                                zIndex: 99999,
                                                maxHeight: '250px',
                                                overflowY: 'auto',
                                                padding: '0',
                                                margin: '5px 0 0 0',
                                                listStyle: 'none'
                                            }}>
                                                {skillResults.map(s => (
                                                    <li
                                                        key={s.id}
                                                        role="option"
                                                        onMouseDown={(e) => {
                                                            e.preventDefault();
                                                            addSkill(s);
                                                        }}
                                                        style={{
                                                            padding: '12px 15px',
                                                            cursor: 'pointer',
                                                            fontSize: '14px',
                                                            borderBottom: '1px solid #eee',
                                                            color: '#333',
                                                            backgroundColor: '#fff'
                                                        }}
                                                        onMouseOver={(e) => e.currentTarget.style.backgroundColor = '#fff5f5'}
                                                        onMouseOut={(e) => e.currentTarget.style.backgroundColor = '#fff'}
                                                    >
                                                        {s.name}
                                                    </li>
                                                ))}
                                            </ul>
                                        )}
                                    </div>
                                    <button
                                        className="search-button"
                                        style={{
                                            padding: '0 15px',
                                            backgroundColor: '#ff6b6b',
                                            color: '#fff',
                                            borderRadius: '8px',
                                            border: 'none',
                                            cursor: 'pointer'
                                        }}
                                        onClick={() => {
                                            if (skillResults.length > 0) {
                                                addSkill(skillResults[0]);
                                            } else {
                                                alert("검색 결과가 없습니다. 목록에서 선택해 주세요.");
                                            }
                                        }}
                                    >추가</button>
                                </div>
                            </div>
                        )}
                    </div>
                </section>

                {/* 희망 기업 섹션 */}
                <section className="profile-card">
                    <div className="card-header">
                        <h2 className="card-title">희망 기업</h2>
                        <MdBusiness className="header-icon" />
                    </div>
                    <div className="company-tags">
                        {profile.companies.map((c, idx) => (
                            <span key={`${c.name}-${idx}`} className="company-tag">
                                {c.name || c.id}
                                {isEditing && (
                                    <span
                                        className="tag-remove"
                                        onClick={() => setProfile({ ...profile, companies: profile.companies.filter((_, i) => i !== idx) })}
                                    >✕</span>
                                )}
                            </span>
                        ))}
                    </div>

                    {isEditing && (
                        <div className="company-search" style={{ position: 'relative', marginTop: '20px' }}>
                            <p className="stack-label">취업을 희망하는 기업을 추가해주세요.</p>
                            <div className="search-bar" style={{ position: 'relative', display: 'flex', gap: '10px' }}>
                                <div className="search-input-wrapper" style={{ position: 'relative', flex: 1 }}>
                                    <input
                                        type="text"
                                        placeholder="기업명을 입력해주세요."
                                        value={companySearch}
                                        onChange={(e) => setCompanySearch(e.target.value)}
                                        style={{
                                            width: '100%',
                                            padding: '12px',
                                            borderRadius: '8px',
                                            border: '1px solid #ff6b6b',
                                            fontSize: '14px',
                                            boxSizing: 'border-box'
                                        }}
                                    />
                                    {(isCompanyLoading || (companySearch.trim() && companyResults.length >= 0)) && companySearch.trim() && (
                                        <ul role="listbox" style={{
                                            position: 'absolute', top: '100%', left: 0, right: 0,
                                            backgroundColor: '#ffffff', border: '2px solid #ff6b6b',
                                            borderRadius: '8px', boxShadow: '0 10px 25px rgba(0,0,0,0.2)',
                                            zIndex: 999999, maxHeight: '250px', overflowY: 'auto',
                                            padding: '0', margin: '5px 0 0 0', listStyle: 'none'
                                        }}>
                                            {isCompanyLoading ? (
                                                <li style={{ padding: '15px', color: '#999', textAlign: 'center', fontSize: '14px' }}>검색 중...</li>
                                            ) : (
                                                <>
                                                    {companyResults.length > 0 ? (
                                                        companyResults.map(c => (
                                                            <li
                                                                key={c.id}
                                                                role="option"
                                                                onMouseDown={(e) => {
                                                                    e.preventDefault();
                                                                    addCompany(c);
                                                                }}
                                                                style={{
                                                                    padding: '12px 15px', cursor: 'pointer',
                                                                    fontSize: '14px', borderBottom: '1px solid #eee',
                                                                    color: '#333', backgroundColor: '#fff'
                                                                }}
                                                                onMouseOver={(e) => e.currentTarget.style.backgroundColor = '#fff5f5'}
                                                                onMouseOut={(e) => e.currentTarget.style.backgroundColor = '#fff'}
                                                            >
                                                                {c.name}
                                                            </li>
                                                        ))
                                                    ) : (
                                                        <li style={{ padding: '15px', color: '#999', textAlign: 'center', fontSize: '14px' }}>결과가 없습니다.</li>
                                                    )}
                                                </>
                                            )}
                                        </ul>
                                    )}
                                </div>
                                <button
                                    className="search-button"
                                    style={{
                                        padding: '0 15px', backgroundColor: '#ff6b6b',
                                        color: '#fff', borderRadius: '8px', border: 'none', cursor: 'pointer'
                                    }}
                                    onClick={() => {
                                        if (companyResults.length > 0) {
                                            addCompany(companyResults[0]);
                                        } else if (companySearch.trim()) {
                                            showAlert('error', '기업 선택 필요', '검색 결과에서 기업을 선택해 주세요.');
                                        }
                                    }}
                                >추가</button>
                            </div>
                        </div>
                    )}
                </section>

                <div className="footer-actions">
                    {isEditing ? (
                        <button className="submit-button" onClick={handleSave}>완료</button>
                    ) : (
                        <button className="edit-link" onClick={handleEditToggle}>수정하기</button>
                    )}
                </div>
            </main>

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

export default ProfilePage;
