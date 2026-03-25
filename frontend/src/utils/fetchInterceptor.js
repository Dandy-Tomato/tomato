const { fetch: originalFetch } = window;
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8080';

let isRefreshing = false;
let failedQueue = [];

const processQueue = (error, token = null) => {
    failedQueue.forEach(prom => {
        if (error) {
            prom.reject(error);
        } else {
            prom.resolve(token);
        }
    });
    failedQueue = [];
};

window.fetch = async (...args) => {
    let [resource, config] = args;
    
    // 1. 원래 요청 수행
    let response = await originalFetch(resource, config);

    const urlStr = typeof resource === 'string' ? resource : resource?.url || '';
    
    // 2. 401 에러 발생 & 갱신 제외 대상 API 여부 체크
    if (response.status === 401 && !urlStr.includes('/auth/login') && !urlStr.includes('/auth/refresh') && !urlStr.includes('/auth/signup') && !urlStr.includes('/auth/check-email')) {
        const refreshToken = localStorage.getItem('refreshToken');
        
        // 리프레시 토큰이 없으면 즉시 로그아웃 처리
        if (!refreshToken) {
            localStorage.clear();
            window.location.href = '/login';
            return response;
        }

        // 이미 토큰 갱신 로직이 돌고 있다면, 큐에 대기시켰다가 끝나면 재시도
        if (isRefreshing) {
            return new Promise((resolve, reject) => {
                failedQueue.push({ resolve, reject });
            }).then(token => {
                const newConfig = config ? { ...config } : {};
                newConfig.headers = {
                    ...(newConfig.headers || {}),
                    'Authorization': `Bearer ${token}`
                };
                return originalFetch(resource, newConfig);
            }).catch(err => {
                return response;
            });
        }

        isRefreshing = true;

        try {
            // 새 토큰 발급 요청
            const refreshResponse = await originalFetch(`${API_BASE_URL}/auth/refresh`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ refreshToken })
            });

            if (refreshResponse.ok) {
                const result = await refreshResponse.json();
                const newAccessToken = result.data.accessToken;
                const newRefreshToken = result.data.refreshToken;

                // 스토리지 업데이트
                localStorage.setItem('accessToken', newAccessToken);
                localStorage.setItem('refreshToken', newRefreshToken);

                // 대기 중이던 큐의 요청들에게 새 토큰 전달
                processQueue(null, newAccessToken);

                // 현재 실패했던 요청도 새 토큰으로 재발송
                const newConfig = config ? { ...config } : {};
                newConfig.headers = {
                    ...(newConfig.headers || {}),
                    'Authorization': `Bearer ${newAccessToken}`
                };
                response = await originalFetch(resource, newConfig);
            } else {
                // 리프레시 토큰 만료/올바르지 않음 -> 다시 로그인 필요
                processQueue(new Error('Refresh token invalid'));
                localStorage.clear();
                window.location.href = '/login';
            }
        } catch (error) {
            processQueue(error);
            localStorage.clear();
            window.location.href = '/login';
        } finally {
            isRefreshing = false;
        }
    }

    return response;
};
