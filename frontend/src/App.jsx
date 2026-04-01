import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import LoginPage from './pages/Login/LoginPage';
import CallbackPage from './pages/Callback/CallbackPage';
import MainPage from './pages/Main/MainPage';
import SignupPage from './pages/Signup/SignupPage';
import ProfilePage from './pages/Profile/ProfilePage';
import ProjectCreatePage from './pages/ProjectCreate/ProjectCreatePage';
import ProjectDetailPage from './pages/ProjectDetail/ProjectDetailPage';
import ScrollToTop from './components/common/ScrollToTop';
import ProtectedRoute from './components/common/ProtectedRoute';

function App() {
    return (
        // Router 설정: URL 변경에 따른 전반적인 브라우저 라우팅을 관리합니다.
        <Router>
            {/* 페이지 이동 시 스크롤을 최상단으로 올려주는 공통 컴포넌트 */}
            <ScrollToTop />
            <div className="App">
                {/* 주어진 URL 경로(path)에 따라 적절한 컴포넌트(element)를 렌더링합니다. */}
                <Routes>
                    {/* 퍼블릭 라우트 */}
                    <Route path="/" element={<LoginPage />} />
                    <Route path="/oauth/callback" element={<CallbackPage />} />
                    <Route path="/signup" element={<SignupPage />} />
                    
                    {/* 보호된 라우트: 로그인이 된 인증 사용자만 접근할 수 있는 페이지들 */}
                    <Route path="/main" element={<ProtectedRoute><MainPage /></ProtectedRoute>} />
                    <Route path="/profile" element={<ProtectedRoute><ProfilePage /></ProtectedRoute>} />
                    <Route path="/projects/create" element={<ProtectedRoute><ProjectCreatePage /></ProtectedRoute>} />
                    <Route path="/projects/:projectId" element={<ProtectedRoute><ProjectDetailPage /></ProtectedRoute>} />
                </Routes>
            </div>
        </Router>
    );
}

export default App;
