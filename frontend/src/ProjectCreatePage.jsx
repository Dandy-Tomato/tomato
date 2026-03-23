import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Navbar from './components/Navbar';
import './ProjectCreatePage.css';
import { SKILLS, DOMAINS } from './constants';
import { MdFolder, MdEdit, MdHandyman, MdShoppingBag, MdCalendarMonth, MdExpandMore } from 'react-icons/md';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8080';

const ProjectCreatePage = () => {
    const navigate = useNavigate();
    const [formData, setFormData] = useState({
        name: '',
        description: '',
        startedAt: '',
        dueAt: '',
        techSkillIds: [],
        domainIds: []
    });

    const [skillSearch, setSkillSearch] = useState('');
    const [skillResults, setSkillResults] = useState([]);
    const [isSkillDropdownOpen, setIsSkillDropdownOpen] = useState(false);

    useEffect(() => {
        if (skillSearch.trim()) {
            const filtered = SKILLS.filter(s =>
                s.name.toLowerCase().includes(skillSearch.toLowerCase()) &&
                !formData.techSkillIds.includes(s.id)
            );
            setSkillResults(filtered.slice(0, 5));
        } else {
            setSkillResults([]);
        }
    }, [skillSearch, formData.techSkillIds]);

    const handleInputChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({ ...prev, [name]: value }));
    };

    const addSkill = (skill) => {
        setFormData(prev => ({
            ...prev,
            techSkillIds: [...prev.techSkillIds, skill.id]
        }));
        setSkillSearch('');
        setIsSkillDropdownOpen(false);
    };

    const removeSkill = (skillId) => {
        setFormData(prev => ({
            ...prev,
            techSkillIds: prev.techSkillIds.filter(id => id !== skillId)
        }));
    };

    const toggleDomain = (domainId) => {
        setFormData(prev => {
            const isSelected = prev.domainIds.includes(domainId);
            if (isSelected) {
                return { ...prev, domainIds: prev.domainIds.filter(id => id !== domainId) };
            } else {
                return { ...prev, domainIds: [...prev.domainIds, domainId] };
            }
        });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        
        if (!formData.name || !formData.description || !formData.startedAt || !formData.dueAt) {
            alert("필수 정보를 모두 입력해 주세요.");
            return;
        }

        const token = localStorage.getItem("accessToken");
        if (!token) {
            alert("로그인이 필요합니다.");
            navigate('/');
            return;
        }

        const body = {
            ...formData,
            techSkillIds: formData.techSkillIds.map(id => Number(id)),
            domainIds: formData.domainIds.map(id => Number(id))
        };

        try {
            const response = await fetch(`${API_BASE_URL}/projects`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify(body)
            });

            const result = await response.json();
            if (response.ok) {
                alert("프로젝트가 성공적으로 생성되었습니다!");
                navigate('/main');
            } else {
                alert(result.message || "프로젝트 생성에 실패했습니다.");
            }
        } catch (error) {
            console.error("Error creating project:", error);
            alert("서버 오류가 발생했습니다.");
        }
    };

    const getSkillName = (id) => SKILLS.find(s => s.id === id)?.name || id;

    return (
        <div className="project-create-page">
            <Navbar />
            <main className="project-create-content">
                <header className="page-header">
                    <h1 className="page-title">프로젝트 생성/수정</h1>
                </header>
                
                <div className="create-card">
                    <form onSubmit={handleSubmit} className="project-form">
                        
                        {/* 프로젝트명 */}
                        <div className="form-section">
                            <div className="section-label">
                                <MdFolder className="section-icon" /> 프로젝트명
                            </div>
                            <input 
                                type="text" 
                                name="name"
                                className="form-input" 
                                placeholder="프로젝트명을 입력하세요."
                                value={formData.name}
                                onChange={handleInputChange}
                                required
                            />
                        </div>

                        {/* 프로젝트 설명 */}
                        <div className="form-section">
                            <div className="section-label">
                                <MdEdit className="section-icon" /> 프로젝트 설명
                            </div>
                            <textarea 
                                name="description"
                                className="form-textarea" 
                                placeholder="프로젝트에 대한 설명을 입력하세요."
                                value={formData.description}
                                onChange={handleInputChange}
                                required
                            ></textarea>
                        </div>

                        {/* 희망 기술 스택 */}
                        <div className="form-section">
                            <div className="section-label">
                                <MdHandyman className="section-icon" /> 희망 기술 스택
                            </div>
                            <div className="selected-tags">
                                {formData.techSkillIds.map(id => (
                                    <span key={id} className="tech-tag">
                                        {getSkillName(id)}
                                        <span className="tag-remove" onClick={() => removeSkill(id)}>✕</span>
                                    </span>
                                ))}
                            </div>
                            <div className="dropdown-container">
                                <div className="custom-dropdown" onClick={() => setIsSkillDropdownOpen(!isSkillDropdownOpen)}>
                                    <span>{skillSearch || "기술 스택"}</span>
                                    <MdExpandMore className={`arrow-icon ${isSkillDropdownOpen ? 'open' : ''}`} />
                                </div>
                                {isSkillDropdownOpen && (
                                    <div className="dropdown-menu">
                                        <input 
                                            type="text" 
                                            className="dropdown-search"
                                            placeholder="검색..."
                                            value={skillSearch}
                                            onChange={(e) => setSkillSearch(e.target.value)}
                                            autoFocus
                                            onClick={(e) => e.stopPropagation()}
                                        />
                                        <ul className="dropdown-list">
                                            {skillResults.length > 0 ? (
                                                skillResults.map(s => (
                                                    <li key={s.id} onClick={() => addSkill(s)}>{s.name}</li>
                                                ))
                                            ) : (
                                                <li className="no-result">결과 없음</li>
                                            )}
                                        </ul>
                                    </div>
                                )}
                            </div>
                        </div>

                        {/* 희망 도메인 */}
                        <div className="form-section">
                            <div className="section-label">
                                <MdShoppingBag className="section-icon" /> 희망 도메인
                            </div>
                            <div className="domain-tags-container">
                                {DOMAINS.map(domain => (
                                    <div 
                                        key={domain.id} 
                                        className={`domain-tag ${formData.domainIds.includes(domain.id) ? 'active' : ''}`}
                                        onClick={() => toggleDomain(domain.id)}
                                    >
                                        {domain.name}
                                    </div>
                                ))}
                            </div>
                        </div>

                        {/* 프로젝트 기간 */}
                        <div className="form-section">
                            <div className="section-label">
                                <MdCalendarMonth className="section-icon" /> 프로젝트 기간
                            </div>
                            <div className="date-picker-row">
                                <div className="date-input-wrapper">
                                    <input 
                                        type="date" 
                                        name="startedAt"
                                        className="custom-date-picker" 
                                        value={formData.startedAt}
                                        onChange={handleInputChange}
                                        required
                                    />
                                </div>
                                <span className="date-sep">~</span>
                                <div className="date-input-wrapper">
                                    <input 
                                        type="date" 
                                        name="dueAt"
                                        className="custom-date-picker" 
                                        value={formData.dueAt}
                                        onChange={handleInputChange}
                                        required
                                    />
                                </div>
                            </div>
                        </div>

                        <button type="submit" className="huge-submit-button">생성하기</button>
                    </form>
                </div>
            </main>
        </div>
    );
};

export default ProjectCreatePage;
