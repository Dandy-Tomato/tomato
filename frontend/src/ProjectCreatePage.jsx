import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Navbar from './components/Navbar';
import './ProjectCreatePage.css';
import { SKILLS, DOMAINS } from './constants';
import { MdFolder, MdEdit, MdHandyman, MdShoppingBag, MdCalendarMonth, MdExpandMore } from 'react-icons/md';
import AlertModal from './components/AlertModal';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8080';

const ProjectCreatePage = () => {
    const navigate = useNavigate();
    const queryParams = new URLSearchParams(window.location.search);
    const editProjectId = queryParams.get('edit');
    const isEditMode = !!editProjectId;

    const [formData, setFormData] = useState({
        name: '',
        description: '',
        startedAt: '',
        dueAt: '',
        techSkillIds: [],
        domainIds: []
    });
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

    const [loading, setLoading] = useState(isEditMode);

    const [skillSearch, setSkillSearch] = useState('');
    const [skillResults, setSkillResults] = useState([]);

    useEffect(() => {
        if (isEditMode) {
            fetchProjectForEdit();
        }
    }, [editProjectId]);

    const fetchProjectForEdit = async () => {
        const token = localStorage.getItem("accessToken");
        try {
            const response = await fetch(`${API_BASE_URL}/projects/${editProjectId}`, {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            const result = await response.json();
            if (response.ok && result.data) {
                const d = result.data;
                setFormData({
                    name: d.name,
                    description: d.description,
                    startedAt: d.startedAt,
                    dueAt: d.dueAt,
                    techSkillIds: d.techSkillIds || [],
                    domainIds: d.domains || []
                });
            }
        } catch (error) {
            console.error("Error fetching project for edit:", error);
        } finally {
            setLoading(false);
        }
    };

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
            showAlert('error', '입력 오류', '필수 정보를 모두 입력해 주세요.');
            return;
        }

        const token = localStorage.getItem("accessToken");
        if (!token) {
            showAlert('error', '로그인 필요', '로그인이 필요합니다.', () => navigate('/'));
            return;
        }

        const body = {
            ...formData,
            techSkillIds: formData.techSkillIds.map(id => Number(id)),
            domainIds: formData.domainIds.map(id => Number(id))
        };

        try {
            const url = isEditMode ? `${API_BASE_URL}/projects/${editProjectId}` : `${API_BASE_URL}/projects`;
            const method = isEditMode ? 'PATCH' : 'POST';

            const response = await fetch(url, {
                method: method,
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify(body)
            });

            const result = await response.json();
            if (response.ok) {
                showAlert('success', '완료', isEditMode ? "프로젝트가 성공적으로 수정되었습니다!" : "프로젝트가 성공적으로 생성되었습니다!", 
                    () => navigate(isEditMode ? `/projects/${editProjectId}` : '/main'));
            } else {
                showAlert('error', '오류', result.message || "작업에 실패했습니다.");
            }
        } catch (error) {
            console.error("Error creating project:", error);
            showAlert('error', '서버 오류', "서버 오류가 발생했습니다.");
        }
    };

    if (loading) return <div className="loading">로딩 중...</div>;

    const getSkillName = (id) => SKILLS.find(s => s.id === id)?.name || id;

    return (
        <div className="project-create-page">
            <Navbar />
            <main className="project-create-content">
                <header className="page-header">
                    <h1 className="page-title">프로젝트 {isEditMode ? '수정' : '생성'}</h1>
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
                            <div className="input-with-button">
                                <div className="input-wrapper relative" style={{ flex: 1, position: 'relative' }}>
                                    <input 
                                        type="text" 
                                        className="form-input" 
                                        placeholder="기술 스택 검색 (예: Java, React)"
                                        value={skillSearch}
                                        onChange={(e) => setSkillSearch(e.target.value)}
                                    />
                                    {skillSearch.trim() && (
                                        <div className="search-results-container">
                                            <ul className="search-results-list">
                                                {skillResults.length > 0 ? (
                                                    skillResults.map(s => (
                                                        <li key={s.id} className="result-item" onClick={() => addSkill(s)}>
                                                            {s.name}
                                                        </li>
                                                    ))
                                                ) : (
                                                    <li className="no-result">결과 없음</li>
                                                )}
                                            </ul>
                                        </div>
                                    )}
                                </div>
                                <button 
                                    type="button" 
                                    className="add-button"
                                    onClick={() => {
                                        if (skillResults.length > 0) {
                                            addSkill(skillResults[0]);
                                        } else if (skillSearch.trim()) {
                                            showAlert('info', '검색 결과 없음', '검색 결과가 없습니다. 목록에서 선택해 주세요.');
                                        }
                                    }}
                                >
                                    추가
                                </button>
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

                        <button type="submit" className="huge-submit-button">{isEditMode ? '수정하기' : '생성하기'}</button>
                    </form>
                </div>
            </main>
            <AlertModal 
                isOpen={modal.isOpen}
                type={modal.type}
                title={modal.title}
                message={modal.message}
                onClose={() => setModal(prev => ({ ...prev, isOpen: false }))}
                onConfirm={modal.onConfirm}
            />
        </div>
    );
};

export default ProjectCreatePage;
