import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import Navbar from './components/Navbar';
import './ProjectDetailPage.css';
import { SKILLS, DOMAINS, POSITIONS } from './constants';
import {
    MdEdit, MdContentCopy, MdKeyboardArrowDown, MdKeyboardArrowUp,
    MdAutoAwesome, MdSearch, MdBookmarkBorder, MdBookmark,
    MdAdd, MdPeopleOutline, MdPersonAdd, MdThumbUp, MdThumbDown,
    MdArrowBack, MdRefresh, MdLightbulbOutline
} from 'react-icons/md';
import AlertModal from './components/AlertModal';
import ReactMarkdown from 'react-markdown';


const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8080';

// 주제 상세 보기 컴포넌트
const TopicDetailView = ({
    topic,
    isLoading,
    onBack,
    onReaction,
    onBookmark,
    getDomainName,
    getSkillName,
    onRefine,
    isRefined, // state from parent if needed, but we use topic.childTopics
    isRefining,
    confirmedChildTopicId,
    onConfirmTopic,
    onUnconfirmTopic,
    isOwner
}) => {
    const [expandedChildId, setExpandedChildId] = useState(null);

    if (isLoading || !topic) return <div className="topic-detail-loading">데이터를 불러오는 중...</div>;

    const isMarked = topic.isBookmarked === true || topic.isBookmarked === 'true' ||
        topic.isBookmark === true || topic.isBookmark === 'true' ||
        topic.bookmarked === true || topic.bookmarked === 'true';

    const toggleChild = (id) => {
        setExpandedChildId(expandedChildId === id ? null : id);
    };

    return (
        <div className="topic-detail-view">
            {/* 상단 헤더 섹션 */}
            <div className="topic-detail-header-card">
                <div className="topic-header-top">
                    <span className="topic-domain-badge">{getDomainName(topic.domainId)}</span>
                    <div className="topic-actions">
                        <button
                            className={`topic-action-btn ${topic.isReaction === 'LIKE' ? 'active' : ''}`}
                            onClick={() => onReaction(topic.topicId, 'LIKE')}
                        >
                            <MdThumbUp />
                        </button>
                        <button
                            className={`topic-action-btn ${topic.isReaction === 'DISLIKE' ? 'active' : ''}`}
                            onClick={() => onReaction(topic.topicId, 'DISLIKE')}
                        >
                            <MdThumbDown />
                        </button>
                        <button
                            className={`topic-action-btn bookmark ${isMarked ? 'active' : ''}`}
                            onClick={() => onBookmark(topic.topicId)}
                        >
                            {isMarked ? <MdBookmark style={{ color: '#ee7c62' }} /> : <MdBookmarkBorder />}
                        </button>
                    </div>
                </div>

                <h1 className="topic-detail-title">{topic.title}</h1>

                <div className="topic-detail-skills">
                    {topic.skills.map(id => (
                        <span key={id} className="td-skill-tag">{getSkillName(id)}</span>
                    ))}
                </div>

                <p className="topic-detail-description">{topic.description}</p>

                <div className="topic-metadata-grid">
                    <div className="metadata-item">
                        <span className="meta-label">예상 개발 기간</span>
                        <div className="metadata-value-wrap">
                            <span className="meta-icon">📅</span>
                            <span className="meta-value">{topic.expectedDurationWeek || 0}주</span>
                        </div>
                    </div>
                    <div className="metadata-item">
                        <span className="meta-label">추천 팀원 수</span>
                        <div className="metadata-value-wrap">
                            <span className="meta-icon">👥</span>
                            <span className="meta-value">{topic.recommendedTeamSize || 0}명</span>
                        </div>
                    </div>
                </div>
            </div>

            {/* 이동 및 구체화 버튼 섹션 */}
            <div className="topic-nav-actions">
                <p className="nav-info-text">마음에 드신다면 AI로 주제를 더 구체화해보세요!</p>
                <div className="nav-buttons">
                    <button className="back-to-list-btn" onClick={onBack}>
                        <MdArrowBack className="btn-icon" /> 목록으로
                    </button>
                    <button
                        className="elaborate-btn"
                        onClick={() => onRefine(topic.topicId)}
                        disabled={isRefining}
                    >
                        <MdAutoAwesome className="btn-icon" /> {isRefining ? '생성 중...' : '구체화하기'}
                    </button>
                </div>
            </div>

            {/* 구체화 결과 섹션 (childTopics 데이터가 있을 경우 표시) */}
            {topic.childTopics && topic.childTopics.length > 0 && (
                <div className="elaboration-section">
                    <div className="elab-badge-row">
                        <span className="elab-status-badge"><MdAutoAwesome /> 구체화 목록</span>
                    </div>

                    <div className="child-topics-list">
                        {topic.childTopics.map((child) => {
                            const isConfirmed = Number(child.childTopicId) === Number(confirmedChildTopicId);

                            return (
                                <div key={child.childTopicId} className={`child-topic-item ${expandedChildId === child.childTopicId ? 'expanded' : ''} ${isConfirmed ? 'confirmed' : ''}`}>
                                    <div
                                        className="child-topic-header"
                                        onClick={() => toggleChild(child.childTopicId)}
                                    >
                                        <div className="child-topic-title-wrap">
                                            <h3 className="child-topic-title">{child.title}</h3>
                                            {isConfirmed && <span className="confirmed-badge">확정됨</span>}
                                        </div>
                                        <div className="child-topic-actions">
                                            {isOwner && (
                                                isConfirmed ? (
                                                    <button
                                                        className="unconfirm-btn"
                                                        onClick={(e) => {
                                                            e.stopPropagation();
                                                            onUnconfirmTopic();
                                                        }}
                                                    >
                                                        확정 해제
                                                    </button>
                                                ) : (
                                                    <button
                                                        className="confirm-btn"
                                                        onClick={(e) => {
                                                            e.stopPropagation();
                                                            onConfirmTopic(child.childTopicId);
                                                        }}
                                                    >
                                                        주제 확정
                                                    </button>
                                                )
                                            )}
                                            {expandedChildId === child.childTopicId ? <MdKeyboardArrowUp /> : <MdKeyboardArrowDown />}
                                        </div>
                                    </div>
                                    {expandedChildId === child.childTopicId && (
                                        <div className="child-topic-content markdown-body">
                                            <ReactMarkdown>{child.content}</ReactMarkdown>
                                        </div>
                                    )}
                                </div>
                            );
                        })}
                    </div>

                    <div className="elab-footer">
                        <button className="re-elaborate-btn" onClick={() => onRefine(topic.topicId)} disabled={isRefining}>
                            <MdRefresh className="btn-icon" /> {isRefining ? '생성 중...' : '추가 구체화'}
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
};


const ProjectDetailPage = () => {
    const { projectId } = useParams();
    const navigate = useNavigate();
    const [project, setProject] = useState(null);
    const [loading, setLoading] = useState(true);
    const [isDetailsOpen, setIsDetailsOpen] = useState(true);
    const [activeTab, setActiveTab] = useState('추천 주제');
    const [recommendations, setRecommendations] = useState([]);
    const [isFetchingMore, setIsFetchingMore] = useState(false);
    const [selectedTopicId, setSelectedTopicId] = useState(null);
    const [topicDetail, setTopicDetail] = useState(null);
    const [localBookmarks, setLocalBookmarks] = useState(() => {
        try {
            return new Set(JSON.parse(localStorage.getItem('local_bookmarks') || '[]'));
        } catch { return new Set(); }
    });
    const [isTopicLoading, setIsTopicLoading] = useState(false);
    const [isRefining, setIsRefining] = useState(false);

    const [modal, setModal] = useState({
        isOpen: false,
        type: 'success',
        title: '',
        message: '',
        onConfirm: null,
        showCancel: false
    });

    // 타 사용자 프로필 모달 상태
    const [selectedUser, setSelectedUser] = useState(null);
    const [isUserModalOpen, setIsUserModalOpen] = useState(false);
    const [isUserLoading, setIsUserLoading] = useState(false);

    const showAlert = (type, title, message, onConfirm = null, showCancel = false) => {
        setModal({ isOpen: true, type, title, message, onConfirm, showCancel });
    };

    // 브라우저 뒤로가기 버튼으로 주제 상세 화면을 빠져나올 수 있도록 popstate 처리
    useEffect(() => {
        const handlePopState = () => {
            setSelectedTopicId(null);
        };
        window.addEventListener('popstate', handlePopState);
        return () => window.removeEventListener('popstate', handlePopState);
    }, []);

    // 주제 상세 화면으로 진입 시 dummy hash를 pushState하여 history 스택에 로컬 움직임을 저장
    const openTopicDetail = (topicId) => {
        window.history.pushState({ topicDetail: true }, '');
        setSelectedTopicId(topicId);
    };

    const currentUserId = Number(localStorage.getItem('userId'));

    useEffect(() => {
        fetchProjectDetail();
        fetchRecommendations();
    }, [projectId]);

    useEffect(() => {
        if (selectedTopicId) {
            fetchTopicDetail(selectedTopicId);
        } else {
            setTopicDetail(null);
        }
    }, [selectedTopicId]);

    const fetchProjectDetail = async () => {
        const token = localStorage.getItem("accessToken");
        try {
            const response = await fetch(`${API_BASE_URL}/projects/${projectId}`, {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            const result = await response.json();
            if (response.ok && result.data) {
                console.log("Fetched Project Detail:", result.data);
                console.log("Project Members:", result.data.members);
                setProject(result.data);
            } else {
                showAlert('error', '오류', "프로젝트 정보를 불러오지 못했습니다.", () => navigate('/main'));
            }
        } catch (error) {
            console.error("Error fetching project detail:", error);
        } finally {
            setLoading(false);
        }
    };

    const fetchRecommendations = async (isLoadMore = false) => {
        if (isLoadMore) setIsFetchingMore(true);

        const token = localStorage.getItem("accessToken");
        try {
            // 단순 GET 요청을 반복 호출하면 새로운 추천 주제를 계속 받아오도록 무한 스크롤 형태 전송
            const response = await fetch(`${API_BASE_URL}/projects/${projectId}/recommendations`, {
                headers: { 'Authorization': `Bearer ${token}` }
            });

            // 추가: 상세 조회와 동일하게 403, 404, 500 에러 처리
            if (response.status === 403) {
                showAlert('error', '권한 없음', '해당 프로젝트에 접근 권한이 없습니다.', () => navigate('/main'));
                if (isLoadMore) setIsFetchingMore(false);
                return;
            } else if (response.status === 404) {
                showAlert('error', '오류', '프로젝트를 찾을 수 없습니다.', () => navigate('/main'));
                if (isLoadMore) setIsFetchingMore(false);
                return;
            } else if (response.status === 500) {
                showAlert('error', '서버 오류', '추천 서버 호출에 실패했습니다.');
                if (isLoadMore) setIsFetchingMore(false);
                return;
            }

            const result = await response.json();
            console.log("Recommendations List API Result:", result);

            if (response.ok && result.data) {
                const dataArray = Array.isArray(result.data)
                    ? result.data
                    : (result.data.content || []);

                if (isLoadMore) {
                    setRecommendations(prev => {
                        const existingIds = new Set(prev.map(t => t.topicId));
                        const uniqueNew = dataArray.filter(t => !existingIds.has(t.topicId));
                        return [...prev, ...uniqueNew];
                    });
                } else {
                    setRecommendations(dataArray);
                }
            }
        } catch (error) {
            console.error("Error fetching recommendations:", error);
        } finally {
            if (isLoadMore) setIsFetchingMore(false);
        }
    };

    const fetchTopicDetail = async (topicId) => {
        setIsTopicLoading(true);
        const token = localStorage.getItem("accessToken");
        try {
            const response = await fetch(`${API_BASE_URL}/projects/${projectId}/recommendations/${topicId}`, {
                headers: { 'Authorization': `Bearer ${token}` }
            });

            if (response.status === 403) {
                showAlert('error', '권한 없음', '해당 프로젝트에 접근 권한이 없습니다.');
                setSelectedTopicId(null);
                return;
            } else if (response.status === 404) {
                showAlert('error', '오류', '프로젝트를 찾을 수 없습니다.');
                setSelectedTopicId(null);
                return;
            } else if (response.status === 500) {
                showAlert('error', '서버 오류', '추천 서버 호출에 실패했습니다.');
                setSelectedTopicId(null);
                return;
            }

            const result = await response.json();
            console.log("Topic Detail API Result:", result);

            if (response.ok && result.data) {
                setTopicDetail(Array.isArray(result.data) ? result.data[0] : result.data);
            } else {
                showAlert('error', '오류', '주제 상세 정보를 불러오지 못했습니다.');
                setSelectedTopicId(null);
            }
        } catch (error) {
            console.error("Error fetching topic detail:", error);
            showAlert('error', '오류', '서버 통신 중 오류가 발생했습니다.');
            setSelectedTopicId(null);
        } finally {
            setIsTopicLoading(false);
        }
    };

    const handleRefine = async (topicId) => {
        setIsRefining(true);
        const token = localStorage.getItem("accessToken");
        try {
            const response = await fetch(`${API_BASE_URL}/projects/${projectId}/refine/${topicId}`, {
                method: 'POST',
                headers: { 'Authorization': `Bearer ${token}` }
            });

            if (response.status === 400) {
                showAlert('error', '입력 오류', '입력값 유효성 검증에 실패했습니다.');
                return;
            } else if (response.status === 409) {
                showAlert('error', '중복 오류', '이미 구체화된 요청이거나 중복 데이터가 존재합니다.');
                return;
            }

            const result = await response.json();
            if (response.ok && result.data) {
                // 기존 childTopics에 새로 생성된 childTopic 추가
                setTopicDetail(prev => ({
                    ...prev,
                    childTopics: [result.data, ...(prev.childTopics || [])]
                }));
                showAlert('success', '구체화 완료', 'AI가 주제를 구체화했습니다. 목록에서 확인해 보세요!');
            } else {
                showAlert('error', '오류', '주제 구체화에 실패했습니다.');
            }
        } catch (error) {
            console.error("Error refining topic:", error);
            showAlert('error', '오류', '서버 통신 중 오류가 발생했습니다.');
        } finally {
            setIsRefining(false);
        }
    };

    const handleConfirmTopic = async (childTopicId) => {
        const token = localStorage.getItem("accessToken");
        try {
            const response = await fetch(`${API_BASE_URL}/projects/${projectId}/confirmed-topic`, {
                method: 'PUT',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ childTopicId })
            });

            if (response.ok) {
                const result = await response.json();
                // 프로젝트 상태 업데이트
                setProject(prev => ({
                    ...prev,
                    confirmedChildTopicId: result.data.confirmedChildTopicId
                }));
                showAlert('success', '주제 확정', '주제가 프로젝트의 최종 테마로 확정되었습니다!');
            } else {
                showAlert('error', '오류', '주제 확정에 실패했습니다.');
            }
        } catch (error) {
            console.error("Error confirming topic:", error);
            showAlert('error', '오류', '서버 통신 중 오류가 발생했습니다.');
        }
    };

    const handleUnconfirmTopic = async () => {
        const token = localStorage.getItem("accessToken");
        try {
            const response = await fetch(`${API_BASE_URL}/projects/${projectId}/confirmed-topic`, {
                method: 'DELETE',
                headers: { 'Authorization': `Bearer ${token}` }
            });

            if (response.ok) {
                // 프로젝트 상태 업데이트
                setProject(prev => ({
                    ...prev,
                    confirmedChildTopicId: null
                }));
                showAlert('info', '확정 해제', '주제 확정이 해제되었습니다.');
            } else {
                showAlert('error', '오류', '주제 확정 해제에 실패했습니다.');
            }
        } catch (error) {
            console.error("Error unconfirming topic:", error);
            showAlert('error', '오류', '서버 통신 중 오류가 발생했습니다.');
        }
    };

    const handleReaction = async (topicId, reactionType) => {


        if (window.isReactionPending) return; // 연속 클릭 방지
        const token = localStorage.getItem("accessToken");
        if (!token) return;

        window.isReactionPending = true;
        try {
            const response = await fetch(`${API_BASE_URL}/projects/${projectId}/topics/${topicId}/reaction`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    reaction: reactionType,
                    // 기존 데이터가 없는 상태(초기 생성)일 때는 무조건 null을 전달
                    version: topicDetail?.isReaction ? (topicDetail?.reactionVersion ?? null) : null
                })
            });

            if (response.ok) {
                const result = await response.json();
                // 전체를 재조회하지 않고 즉시 상태 업데이트 (반응 속도 개선 및 깜빡임 제거)
                setTopicDetail(prev => ({
                    ...prev,
                    isReaction: result.data.isReaction,
                    reactionVersion: result.data.reactionVersion
                }));
                // 목록도 갱신
                setRecommendations(prev => prev.map(t =>
                    t.topicId === topicId ? { ...t, isReaction: result.data.isReaction } : t
                ));
            } else if (response.status === 409) {
                const result = await response.json();
                showAlert('error', '충돌 발생', result.message || '다른 사용자가 먼저 반응을 변경했습니다.');
                fetchTopicDetail(topicId);
            } else {
                showAlert('error', '오류', '반응 처리에 실패했습니다.');
            }
        } catch (error) {
            console.error("Error handling reaction:", error);
            showAlert('error', '오류', '통신 중 오류가 발생했습니다.');
        } finally {
            window.isReactionPending = false;
        }
    };

    const handleBookmarkToggle = async (topicId) => {
        if (window.isBookmarkPending) return; // 연속 클릭 방지
        const token = localStorage.getItem("accessToken");
        if (!token) return;

        window.isBookmarkPending = true;
        try {
            const response = await fetch(`${API_BASE_URL}/projects/${projectId}/topics/${topicId}/bookmark`, {
                method: 'POST',
                headers: { 'Authorization': `Bearer ${token}` }
            });

            if (response.ok) {
                const result = await response.json();

                // 백엔드 API 응답 구조가 Boolean인지 Object인지 판별, 못 찾으면 기존 상태의 무조건 반대값 토글 적용
                let newStatus;
                if (typeof result.data === 'boolean') {
                    newStatus = result.data;
                } else if (result.data !== null && typeof result.data === 'object' && 'isBookmarked' in result.data) {
                    newStatus = result.data.isBookmarked;
                } else {
                    const currentTopic = recommendations.find(t => t.topicId === topicId) || topicDetail;
                    const isCurrentlyMarked = currentTopic?.isBookmarked === true || currentTopic?.isBookmarked === 'true' || currentTopic?.isBookmark === true;
                    newStatus = !isCurrentlyMarked;
                }

                // 목록 상태 즉시 업데이트
                setRecommendations(prev => prev.map(t =>
                    t.topicId === topicId ? { ...t, isBookmarked: newStatus } : t
                ));

                // 상세 보기 상태 즉시 업데이트
                if (selectedTopicId === topicId) {
                    setTopicDetail(prev => ({
                        ...prev,
                        isBookmarked: newStatus
                    }));
                }

                // API 응답 누락 대비 브라우저 캐시에 북마크 상태 강제 저장
                setLocalBookmarks(prev => {
                    const next = new Set(prev);
                    if (newStatus) next.add(topicId);
                    else next.delete(topicId);
                    localStorage.setItem('local_bookmarks', JSON.stringify([...next]));
                    return next;
                });
            } else {
                showAlert('error', '오류', '북마크 처리에 실패했습니다.');
            }
        } catch (error) {
            console.error("Error handling bookmark:", error);
            showAlert('error', '오류', '통신 중 오류가 발생했습니다.');
        } finally {
            window.isBookmarkPending = false;
        }
    };

    const copyInviteCode = async () => {
        const token = localStorage.getItem("accessToken");
        try {
            const response = await fetch(`${API_BASE_URL}/projects/${projectId}/invite-code`, {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            const result = await response.json();
            if (response.ok && result.data?.inviteCode) {
                await navigator.clipboard.writeText(result.data.inviteCode);
                showAlert('success', '복사 완료!', '초대 코드가 클립보드에 복사되었습니다.\n팀원들에게 공유해 보세요.');
            } else {
                showAlert('error', '복사 실패', "초대 코드를 가져오지 못했습니다.");
            }
        } catch (error) {
            console.error("Error fetching invite code:", error);
            showAlert('error', '오류', "초대 코드 복사 중 오류가 발생했습니다.");
        }
    };

    const handleLeaveProject = () => {
        showAlert('info', '프로젝트 나가기', "정말로 이 프로젝트에서 나가시겠습니까?", () => executeLeaveProject(), true);
    };

    const executeLeaveProject = async () => {
        const token = localStorage.getItem("accessToken");
        try {
            const response = await fetch(`${API_BASE_URL}/projects/${projectId}/members`, {
                method: 'DELETE',
                headers: { 'Authorization': `Bearer ${token}` }
            });
            const result = await response.json();

            if (response.ok) {
                showAlert('success', '탈퇴 완료', "프로젝트에서 성공적으로 나갔습니다.", () => navigate('/main'));
            } else {
                showAlert('error', '나가기 실패', result.message || "프로젝트 나가기에 실패했습니다.");
            }
        } catch (error) {
            console.error("Error leaving project:", error);
            showAlert('error', '서버 오류', "서버 오류가 발생했습니다.");
        }
    };

    const fetchUserProfile = async (userId) => {
        setIsUserLoading(true);
        const token = localStorage.getItem("accessToken");
        try {
            const response = await fetch(`${API_BASE_URL}/users/${userId}`, {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            const result = await response.json();
            if (response.ok && result.data) {
                setSelectedUser(result.data);
                setIsUserModalOpen(true);
            } else {
                showAlert('error', '죄송합니다', '사용자 프로필을 불러올 수 없습니다.');
            }
        } catch (error) {
            console.error("Error fetching user profile:", error);
            showAlert('error', '오류', '서버 통신 중 오류가 발생했습니다.');
        } finally {
            setIsUserLoading(false);
        }
    };

    if (loading) return <div className="loading">로딩 중...</div>;
    if (!project) return null;

    const isOwner = project.owner.userId === currentUserId;
    const getDomainName = (id) => DOMAINS.find(d => Number(d.id) === Number(id) || d.name === id || d.dbName === id)?.name || id;

    const getPositionObj = (id) => {
        if (!id) return null;
        // id가 객체로 넘어올 경우를 대비한 정제 로직
        const realId = (id && typeof id === 'object' && !Array.isArray(id))
            ? (id.id || id.positionId || id.position)
            : id;

        if (!realId) return null;

        const numId = Number(realId);
        const found = POSITIONS.find(p =>
            p.id === numId ||
            String(p.id) === String(realId) ||
            (typeof realId === 'string' && (p.name === realId || p.dbName === realId))
        );

        if (!found) {
            console.warn(`Position mapping failed for ID:`, realId, "Raw Input:", id);
        }
        return found;
    };

    const getPositionName = (id) => getPositionObj(id)?.name || '기타';
    const getPositionIcon = (id) => getPositionObj(id)?.icon || '👤';

    const getSkillName = (id) => SKILLS.find(s => Number(s.id) === Number(id) || s.name === id)?.name || id;

    return (
        <div className="project-detail-page">
            <Navbar />
            <main className="project-detail-content">

                {/* 프로젝트 헤더 카드 */}
                <div className="project-header-card">
                    <div className="header-main">
                        <div className="header-left">
                            <div className="title-row" onClick={() => setIsDetailsOpen(!isDetailsOpen)}>
                                <h1 className="project-name">{project.name}</h1>
                                {isDetailsOpen ? <MdKeyboardArrowUp className="toggle-icon" /> : <MdKeyboardArrowDown className="toggle-icon" />}
                            </div>
                            <p className="project-meta">{project.startedAt} - {project.dueAt}</p>
                            <p className="project-description-summary">{project.description}</p>
                        </div>
                        <div className="header-right">
                            <div className="member-count-badge">
                                <MdPeopleOutline className="m-icon" /> <span>{project.memberCount}명</span>
                            </div>
                            <button className="copy-code-button" onClick={copyInviteCode}>
                                <MdPersonAdd className="btn-icon" /> 초대코드 복사하기
                            </button>
                            {isOwner && (
                                <button className="edit-icon-button" onClick={() => navigate(`/projects/create?edit=${projectId}`)}>
                                    <MdEdit />
                                </button>
                            )}
                        </div>
                    </div>

                    {isDetailsOpen && (
                        <div className="header-details">
                            <div className="domain-section">
                                <p className="detail-label">도메인</p>
                                <div className="detail-tags">
                                    {project.domains.map(id => (
                                        <span key={id} className="detail-tag">{getDomainName(id)}</span>
                                    ))}
                                </div>
                            </div>
                            <div className="members-section">
                                <p className="detail-label">참여자</p>
                                <div className="member-cards-grid">
                                    {project.members.map(member => (
                                        <div
                                            key={member.userId}
                                            className="member-small-card clickable"
                                            onClick={() => fetchUserProfile(member.userId)}
                                        >
                                            <span className="m-name">{member.nickname || member.name || '익명'}</span>
                                            <span className="m-pos">{getPositionName(member.positionId || member.position)}</span>
                                        </div>
                                    ))}
                                </div>
                            </div>
                            {!isOwner && (
                                <div className="detail-footer">
                                    <button className="leave-project-link" onClick={handleLeaveProject}>프로젝트 나가기</button>
                                </div>
                            )}
                        </div>
                    )}
                </div>

                {/* 추천 주제 섹션 */}
                <div className="recommend-container">
                    <aside className="recommend-sidebar">
                        <div
                            className={`sidebar-item ${activeTab === '추천 주제' ? 'active' : ''}`}
                            onClick={() => { setActiveTab('추천 주제'); setSelectedTopicId(null); }}
                        >
                            <MdAutoAwesome className="s-icon" /> 추천 주제
                        </div>
                        <div
                            className={`sidebar-item ${activeTab === '북마크' ? 'active' : ''}`}
                            onClick={() => { setActiveTab('북마크'); setSelectedTopicId(null); }}
                        >
                            <MdBookmarkBorder className="s-icon" /> 북마크
                        </div>
                    </aside>

                    <section className="recommend-main">
                        {!selectedTopicId ? (
                            (() => {
                                // 북마크 여부 확인 유틸 함수 (서버 값 다양성 + 로컬 스토리지 백업)
                                const isMarkedTopic = (t) => {
                                    if (!t) return false;
                                    const b = t.isBookmarked ?? t.isBookmark ?? t.bookmarked;
                                    const isServerMarked = b === true || b === 'true' || String(b).toLowerCase() === 'y' || b === 1;
                                    return isServerMarked || localBookmarks.has(t.topicId);
                                };

                                // 현재 탭 상태에 따라 보여줄 목록 필터링
                                const displayRecommendations = activeTab === '북마크'
                                    ? recommendations.filter(isMarkedTopic)
                                    : recommendations;

                                return (
                                    <>
                                        <div className="recommend-header">
                                            <h2 className="recommend-title">{activeTab}</h2>
                                        </div>

                                        {displayRecommendations.length === 0 ? (
                                            <div className="empty-state-message" style={{ textAlign: 'center', padding: '40px', color: '#888' }}>
                                                해당되는 주제가 없거나 북마크가 비어 있습니다.
                                            </div>
                                        ) : (
                                            <div className="topic-grid">
                                                {displayRecommendations.map(topic => {
                                                    const isMarked = isMarkedTopic(topic);

                                                    return (
                                                        <div
                                                            key={topic.topicId}
                                                            className="topic-card clickable"
                                                            onClick={() => openTopicDetail(topic.topicId)}
                                                        >
                                                            <div className="topic-card-header">
                                                                <h3 className="topic-title">{topic.title}</h3>
                                                                <div
                                                                    className="bookmark-btn-wrap"
                                                                    onClick={(e) => {
                                                                        e.stopPropagation();
                                                                        handleBookmarkToggle(topic.topicId);
                                                                    }}
                                                                >
                                                                    {isMarked ? (
                                                                        <MdBookmark className="bookmark-icon active" style={{ color: '#ee7c62' }} />
                                                                    ) : (
                                                                        <MdBookmarkBorder className="bookmark-icon" />
                                                                    )}
                                                                </div>
                                                            </div>
                                                            <div className="topic-domain-tag">{getDomainName(topic.domainId)}</div>
                                                            <div className="topic-footer">
                                                                <div className="topic-skills">
                                                                    {topic.skills.map(s => <span key={s} className="t-skill-tag">{getSkillName(s)}</span>)}
                                                                </div>
                                                            </div>
                                                        </div>
                                                    );
                                                })}
                                            </div>
                                        )}

                                        {/* 북마크 탭이 아닌 추천 탭일 때 계속해서 서버에 더보기를 요청 (새로고침) */}
                                        {activeTab !== '북마크' && (
                                            <div className="more-button-container">
                                                <button
                                                    className="more-btn"
                                                    disabled={isFetchingMore}
                                                    onClick={() => fetchRecommendations(false)}
                                                >
                                                    <MdAutoAwesome className="btn-icon" /> {isFetchingMore ? '추천 주제 생성 중...' : '다시 추천받기'}
                                                </button>
                                            </div>
                                        )}
                                    </>
                                );
                            })()
                        ) : (
                            <TopicDetailView
                                topic={topicDetail}
                                isLoading={isTopicLoading}
                                onBack={() => setSelectedTopicId(null)}
                                onReaction={handleReaction}
                                onBookmark={handleBookmarkToggle}
                                getDomainName={getDomainName}
                                getSkillName={getSkillName}
                                onRefine={handleRefine}
                                isRefining={isRefining}
                                confirmedChildTopicId={project.confirmedChildTopicId}
                                onConfirmTopic={handleConfirmTopic}
                                onUnconfirmTopic={handleUnconfirmTopic}
                                isOwner={isOwner}
                            />



                        )}
                    </section>
                </div>

                <AlertModal
                    isOpen={modal.isOpen}
                    type={modal.type}
                    title={modal.title}
                    message={modal.message}
                    onClose={() => setModal(prev => ({ ...prev, isOpen: false }))}
                    onConfirm={modal.onConfirm}
                    showCancel={modal.showCancel}
                />

                {/* 타 사용자 프로필 모달 */}
                {isUserModalOpen && selectedUser && (
                    <div className="modal-overlay" onClick={() => setIsUserModalOpen(false)}>
                        <div className="user-profile-modal" onClick={(e) => e.stopPropagation()}>
                            <div className="profile-header">
                                <div className="profile-title-wrap">
                                    <h2 className="profile-nickname">{selectedUser.nickname}</h2>
                                </div>
                                <button className="close-x-btn" onClick={() => setIsUserModalOpen(false)}>✕</button>
                            </div>

                            <div className="profile-body">
                                {selectedUser.skillIds && selectedUser.skillIds.length > 0 && (
                                    <div className="profile-info-group">
                                        <p className="p-info-label">보유 기술 스택</p>
                                        <div className="p-skill-tags">
                                            {selectedUser.skillIds.map(id => (
                                                <span key={id} className="p-skill-tag">{getSkillName(id)}</span>
                                            ))}
                                        </div>
                                    </div>
                                )}
                            </div>

                            <button className="profile-close-btn" onClick={() => setIsUserModalOpen(false)}>확인</button>
                        </div>
                    </div>
                )}

                {isUserLoading && (
                    <div className="modal-overlay">
                        <div className="loading-spinner-wrap">
                            <div className="loading-spinner"></div>
                            <p>프로필을 불러오는 중...</p>
                        </div>
                    </div>
                )}
            </main>
        </div>
    );
};

export default ProjectDetailPage;
