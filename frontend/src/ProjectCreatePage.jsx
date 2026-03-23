import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Navbar from './components/Navbar';
import './ProjectCreatePage.css';
import { SKILLS, DOMAINS } from './constants';

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

    useEffect(() => {
        if (skillSearch.trim()) {
            const filtered = SKILLS.filter(s =>
                s.name.toLowerCase().includes(skillSearch.toLowerCase()) &&
                !formData.techSkillIds.includes(s.id)
            );
            setSkillResults(filtered.slice(0, 10));
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
                <div className="create-card">
                    <h1 className="create-title">새 프로젝트 생성</h1>
                    <p className="create-subtitle">함께 프로젝트를 이끌어갈 팀원을 찾아보세요.</p>

                    <form onSubmit={handleSubmit}>
                        <div className="form-group">
                            <label className="form-label">프로젝트명<span className="required-star">*</span></label>
                            <input 
                                type="text" 
                                name="name"
                                className="form-input" 
                                placeholder="프로젝트 이름을 입력하세요."
                                value={formData.name}
                                onChange={handleInputChange}
                                required
                            />
                        </div>

                        <div className="form-group">
                            <label className="form-label">프로젝트 설명<span className="required-star">*</span></label>
                            <textarea 
                                name="description"
                                className="form-textarea" 
                                placeholder="프로젝트에 대해 설명해 주세요. (목표, 진행 방식 등)"
                                value={formData.description}
                                onChange={handleInputChange}
                                required
                            ></textarea>
                        </div>

                        <div className="form-group">
                            <label className="form-label">진행 기간<span className="required-star">*</span></label>
                            <div className="date-range">
                                <input 
                                    type="date" 
                                    name="startedAt"
                                    className="form-input" 
                                    value={formData.startedAt}
                                    onChange={handleInputChange}
                                    required
                                />
                                <span className="date-separator">~</span>
                                <input 
                                    type="date" 
                                    name="dueAt"
                                    className="form-input" 
                                    value={formData.dueAt}
                                    onChange={handleInputChange}
                                    required
                                />
                            </div>
                        </div>

                        <div className="form-group">
                            <label className="form-label">희망 기술 스택</label>
                            <div className="selected-tags">
                                {formData.techSkillIds.map(id => (
                                    <span key={id} className="tag">
                                        {getSkillName(id)}
                                        <span className="tag-remove" onClick={() => removeSkill(id)}>✕</span>
                                    </span>
                                ))}
                            </div>
                            <div className="search-wrapper">
                                <input 
                                    type="text" 
                                    className="form-input" 
                                    placeholder="기술 스택 검색 (예: Java, React)"
                                    value={skillSearch}
                                    onChange={(e) => setSkillSearch(e.target.value)}
                                />
                                {skillResults.length > 0 && (
                                    <ul className="search-results">
                                        {skillResults.map(s => (
                                            <li key={s.id} className="result-item" onClick={() => addSkill(s)}>
                                                {s.name}
                                            </li>
                                        ))}
                                    </ul>
                                )}
                            </div>
                        </div>

                        <div className="form-group">
                            <label className="form-label">산업 도메인<span className="required-star">*</span></label>
                            <div className="domain-grid">
                                {DOMAINS.map(domain => (
                                    <div 
                                        key={domain.id} 
                                        className={`domain-item ${formData.domainIds.includes(domain.id) ? 'active' : ''}`}
                                        onClick={() => toggleDomain(domain.id)}
                                    >
                                        {domain.name}
                                    </div>
                                ))}
                            </div>
                        </div>

                        <div className="create-actions">
                            <button type="button" className="cancel-button" onClick={() => navigate(-1)}>취소</button>
                            <button type="submit" className="submit-button">프로젝트 생성하기</button>
                        </div>
                    </form>
                </div>
            </main>
        </div>
    );
};

export default ProjectCreatePage;
