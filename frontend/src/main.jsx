import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App.jsx';

// 글로벌 스타일시트 및 Fetch 인터셉터 설정 적용
import './styles/index.css';
import './utils/fetchInterceptor.js';

// DOM에서 id가 'root'인 요소를 찾아 React 애플리케이션을 렌더링합니다.
ReactDOM.createRoot(document.getElementById('root')).render(
    // StrictMode: 개발 환경에서 컴포넌트의 잠재적 레거시 이슈, 사이드 이펙트를 감지하기 위해 두 번씩 렌더링합니다.
    <React.StrictMode>
        <App />
    </React.StrictMode>,
);
