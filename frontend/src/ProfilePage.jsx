import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import './ProfilePage.css';
import { MdPerson, MdCode, MdBusiness, MdSearch } from 'react-icons/md';
import { POSITIONS, SKILLS } from './constants';

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
                        const filtered = dataArray.filter(c => !profile.companies.some(pc => pc.id === c.id));
                        setCompanyResults(filtered);
                    } else {
                        console.error("Company search failure (Profile):", result);
                    }
                } catch (error) {
                    console.error("Company search error (Profile):", error);
                }
            } else {
                setCompanyResults([]);
            }
        };

        const timer = setTimeout(fetchCompanies, 300);
        return () => clearTimeout(timer);
    }, [companySearch, profile.companyIds]);

    const fetchProfile = async () => {
        const token = localStorage.getItem("accessToken");
        if (!token) {
            alert("로그인이 필요합니다.");
            window.location.href = "/";
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

                // 직무 ID 매핑 (Number로 강제 변환 및 dbName 매핑 지원)
                let posId = null;
                if (data.position) {
                    if (typeof data.position === 'number') {
                        posId = data.position;
                    } else if (typeof data.position === 'string') {
                        // "frontend", "backend" 등 dbName과 매칭 시도
                        const found = POSITIONS.find(p => p.dbName === data.position || p.name === data.position || String(p.id) === data.position);
                        if (found) posId = Number(found.id);
                        else if (!isNaN(data.position)) posId = Number(data.position);
                    }
                }

                console.log("Full data from Profile API:", data);
                console.log("companyNames from API:", data.companyNames);
                console.log("company_names from API:", data.company_names);
                console.log("companyNameList from API:", data.companyNameList);

                // Use the new names array if available, or fallback to IDs
                const rawNames = data.companyNames || data.companyNameList || data.company_names;
                const rawIds = data.companyIds || data.company_ids || [];

                setProfile({
                    email: data.email || '',
                    nickname: data.nickname || '',
                    githubUsername: data.githubUsername || '',
                    positionId: posId,
                    skillIds: (data.skillIds || []).map(id => Number(id)),
                    companies: rawNames 
                        ? rawNames.map((name, index) => ({ id: Number(rawIds[index]) || index, name }))
                        : rawIds.map(id => ({ id: Number(id), name: `기업 ${id}` }))
                });
                if (data.nickname && data.nickname !== "null") {
                    localStorage.setItem('nickname', data.nickname);
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
            companyIds: profile.companies.map(c => Number(c.id)),
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
                alert("프로필이 수정되었습니다.");
                setIsEditing(false);
                fetchProfile(); // 최신 데이터 다시 불러오기
            } else {
                // 에러 코드 3002(존재하지 않는 직무) 등의 상세 메시지 표시
                const errorMsg = result.message || "수정에 실패했습니다.";
                const errorCode = result.errorCode ? ` (에러 코드: ${result.errorCode})` : "";
                alert(`${errorMsg}${errorCode}\n상태 코드: ${response.status}`);
                console.error("Save failure details:", result);
            }
        } catch (error) {
            console.error("Error updating profile:", error);
            alert("서버 오류가 발생했습니다. 네트워크 상태를 확인해 주세요.");
        }
    };

    if (loading) return <div className="loading">로딩 중...</div>;

    // ID를 이름으로 변환하는 도움 함수들
    const getPositionName = (id) => POSITIONS.find(p => p.id === Number(id))?.name || id || '없음';
    const getSkillName = (id) => SKILLS.find(s => s.id === Number(id))?.name || id;
    const getCompanyName = (id) => id; // Backend currently only returns ID

    const addSkill = (skill) => {
        if (!profile.skillIds.includes(skill.id)) {
            setProfile({ ...profile, skillIds: [...profile.skillIds, skill.id] });
        }
        setSkillSearch('');
    };

    const addCompany = (company) => {
        if (!profile.companies.some(c => c.id === company.id)) {
            setProfile({ ...profile, companies: [...profile.companies, { id: company.id, name: company.name }] });
        }
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
                                    className={`tag-button ${profile.positionId === pos.id ? 'active' : ''}`}
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
                                                top: '100%', // 입력창 바로 아래
                                                left: 0,
                                                right: 0,
                                                backgroundColor: '#ffffff',
                                                border: '2px solid #ff6b6b', // 확실히 보이게 경계 강화
                                                borderRadius: '8px',
                                                boxShadow: '0 10px 25px rgba(0,0,0,0.2)',
                                                zIndex: 99999, // 최상단 노출
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
                                                            console.log("Skill selected:", s);
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
                        {profile.companies.map(c => (
                            <span key={c.id} className="company-tag">
                                {c.name || c.id}
                                {isEditing && (
                                    <span
                                        className="tag-remove"
                                        onClick={() => setProfile({ ...profile, companies: profile.companies.filter(comp => comp.id !== c.id) })}
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
                                            alert("검색 결과에서 기업을 선택해 주세요.");
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
        </div>
    );
};

export default ProfilePage;
