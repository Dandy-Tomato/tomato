import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import LoginPage from './LoginPage';
import CallbackPage from './CallbackPage';
import MainPage from './MainPage';
import SignupPage from './SignupPage';
import ProfilePage from './ProfilePage';
import ProjectCreatePage from './ProjectCreatePage';
import ProjectDetailPage from './ProjectDetailPage';
import ScrollToTop from './components/ScrollToTop';
import ProtectedRoute from './components/ProtectedRoute';

function App() {
    return (
        <Router>
            <ScrollToTop />
            <div className="App">
                <Routes>
                    <Route path="/" element={<LoginPage />} />
                    <Route path="/oauth/callback" element={<CallbackPage />} />
                    
                    {/* 보호된 라우트들 */}
                    <Route path="/main" element={<ProtectedRoute><MainPage /></ProtectedRoute>} />
                    <Route path="/signup" element={<ProtectedRoute><SignupPage /></ProtectedRoute>} />
                    <Route path="/profile" element={<ProtectedRoute><ProfilePage /></ProtectedRoute>} />
                    <Route path="/projects/create" element={<ProtectedRoute><ProjectCreatePage /></ProtectedRoute>} />
                    <Route path="/projects/:projectId" element={<ProtectedRoute><ProjectDetailPage /></ProtectedRoute>} />
                </Routes>
            </div>
        </Router>
    );
}

export default App
