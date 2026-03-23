import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import Navbar from './components/Navbar';
import './ProjectDetailPage.css';
import { SKILLS, DOMAINS, POSITIONS } from './constants';
import { MdEdit, MdDelete, MdContentCopy, MdPeople, MdInfo, MdDateRange, MdLabel } from 'react-icons/md';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8080';

const ProjectDetailPage = () => {
    const { projectId } = useParams();
    const navigate = useNavigate();
    const [project, setProject] = useState(null);
    const [loading, setLoading] = useState(true);
    const [isEditing, setIsEditing] = useState(false);
    const [editData, setEditData] = useState({
        name: '',
        description: '',
        startedAt: '',
        dueAt: '',
        techSkillIds: [],
        domainIds: []
    });

    const currentUserId = Number(localStorage.getItem('userId')); // 로그인 시 저장 필요

    useEffect(() => {
        fetchProjectDetail();
    }, [projectId]);

    const fetchProjectDetail = async () => {
        const token = localStorage.getItem("accessToken");
        try {
            const response = await fetch(`${API_BASE_URL}/projects/${projectId}`, {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            const result = await response.json();
            if (response.ok && result.data) {
                setProject(result.data);
                setEditData({
                    name: result.data.name,
                    description: result.data.description,
                    startedAt: result.data.startedAt,
                    dueAt: result.data.dueAt,
                    techSkillIds: result.data.techSkillIds || [],
                    domainIds: result.data.domains || []
                });
            } else {
                alert("프로젝트 정보를 불러오지 못했습니다.");
                navigate('/main');
            }
        } catch (error) {
            console.error("Error fetching project detail:", error);
        } finally {
            setLoading(false);
        }
    };

    const handleDelete = async () => {
        if (!window.confirm("정말로 이 프로젝트를 삭제하시겠습니까?")) return;

        const token = localStorage.getItem("accessToken");
        try {
            const response = await fetch(`${API_BASE_URL}/projects/${projectId}`, {
                method: 'DELETE',
                headers: { 'Authorization': `Bearer ${token}` }
            });
            if (response.ok) {
                alert("프로젝트가 삭제되었습니다.");
                navigate('/main');
            } else {
                alert("삭제에 실패했습니다.");
            }
        } catch (error) {
            console.error("Error deleting project:", error);
        }
    };

    const handleUpdate = async () => {
        const token = localStorage.getItem("accessToken");
        try {
            const response = await fetch(`${API_BASE_URL}/projects/${projectId}`, {
                method: 'PATCH',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify(editData)
            });
            if (response.ok) {
                alert("프로젝트 정보가 수정되었습니다.");
                setIsEditing(false);
                fetchProjectDetail();
            } else {
                alert("수정에 실패했습니다.");
            }
        } catch (error) {
            console.error("Error updating project:", error);
        }
    };

    const copyInviteCode = () => {
        navigator.clipboard.writeText(project.inviteCode);
        alert("초대 코드가 복사되었습니다.");
    };

    if (loading) return <div className="loading">로딩 중...</div>;
    if (!project) return null;

    const isOwner = project.owner.userId === currentUserId;
    const getDomainName = (id) => DOMAINS.find(d => d.id === id)?.name || id;
    const getPositionName = (id) => POSITIONS.find(p => p.id === id)?.name || 'N/A';

    return (
        <div className="project-detail-page">
            <Navbar />
            <main className="project-detail-content">
                <div className="detail-card">
                    {isEditing ? (
                        <div className="edit-form">
                            <h2>프로젝트 정보 수정</h2>
                            <div className="form-group">
                                <label className="form-label">프로젝트명</label>
                                <input 
                                    className="form-input" 
                                    value={editData.name}
                                    onChange={(e) => setEditData({...editData, name: e.target.value})}
                                />
                            </div>
                            <div className="form-group">
                                <label className="form-label">설명</label>
                                <textarea 
                                    className="form-textarea" 
                                    value={editData.description}
                                    onChange={(e) => setEditData({...editData, description: e.target.value})}
                                />
                            </div>
                            <div className="form-group">
                                <label className="form-label">기간</label>
                                <div className="date-range">
                                    <input type="date" value={editData.startedAt} onChange={(e) => setEditData({...editData, startedAt: e.target.value})}/>
                                    <span>~</span>
                                    <input type="date" value={editData.dueAt} onChange={(e) => setEditData({...editData, dueAt: e.target.value})}/>
                                </div>
                            </div>
                            <div className="form-actions">
                                <button className="cancel-button" onClick={() => setIsEditing(false)}>취소</button>
                                <button className="save-button" onClick={handleUpdate}>저장하기</button>
                            </div>
                        </div>
                    ) : (
                        <>
                            <div className="detail-header">
                                <div className="header-info">
                                    <div className="status-badges">
                                        <span className="badge owner">팀장: {project.owner.nickname}</span>
                                        <span className="badge date">{project.startedAt} ~ {project.dueAt}</span>
                                    </div>
                                    <h1>{project.name}</h1>
                                    <div className="invite-code-wrapper">
                                        <span className="meta-label">초대 코드: </span>
                                        <span className="meta-value">{project.inviteCode}</span>
                                        <button className="copy-button" onClick={copyInviteCode}><MdContentCopy /> 복사</button>
                                    </div>
                                </div>
                                {isOwner && (
                                    <div className="header-actions">
                                        <button className="icon-button" onClick={() => setIsEditing(true)}><MdEdit /></button>
                                        <button className="icon-button delete" onClick={handleDelete}><MdDelete /></button>
                                    </div>
                                )}
                            </div>

                            <section className="detail-section">
                                <h2 className="section-title"><MdInfo /> 프로젝트 설명</h2>
                                <p className="description-text">{project.description}</p>
                            </section>

                            <div className="meta-grid">
                                <section className="detail-section">
                                    <h2 className="section-title"><MdLabel /> 산업 도메인</h2>
                                    <div className="selected-tags">
                                        {project.domains.map(id => (
                                            <span key={id} className="tag">{getDomainName(id)}</span>
                                        ))}
                                    </div>
                                </section>
                                <section className="detail-section">
                                    <h2 className="section-title"><MdPeople /> 참여 멤버 ({project.memberCount}명)</h2>
                                    <div className="members-grid">
                                        {project.members.map(member => (
                                            <div key={member.userId} className="member-card">
                                                <div className="member-avatar">{member.nickname?.[0] || '?'}</div>
                                                <div className="member-info">
                                                    <span className="member-name">{member.nickname || '익명'}</span>
                                                    <span className="member-role">{member.projectRole}</span>
                                                    <span className="member-position">{getPositionName(member.positionId)}</span>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                </section>
                            </div>
                        </>
                    )}
                </div>
            </main>
        </div>
    );
};

export default ProjectDetailPage;
