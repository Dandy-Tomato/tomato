import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import LoginPage from './LoginPage';
import CallbackPage from './CallbackPage';
import MainPage from './MainPage';
import SignupPage from './SignupPage';

function App() {
    return (
        <Router>
            <div className="App">
                <Routes>
                    <Route path="/" element={<LoginPage />} />
                    <Route path="/oauth/callback" element={<CallbackPage />} />
                    <Route path="/main" element={<MainPage />} />
                    <Route path="/signup" element={<SignupPage />} />
                </Routes>
            </div>
        </Router>
    );
}

export default App
