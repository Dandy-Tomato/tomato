const { fetch: originalFetch } = window;
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8080';

// 토큰 갱신 진행 여부 및 대기 중인 요청 큐
let isRefreshing = false;
let failedQueue = [];

/**
 * 갱신 중 실패한 요청들을 다시 처리하기 위해 큐를 순회합니다.
 * @param {Error} error - 토큰 갱신 실패 에러 
 * @param {string} token - 갱신된 새로운 액세스 토큰
 */
const processQueue = (error, token = null) => {
    failedQueue.forEach(prom => {
        if (error) {
            prom.reject(error); // 에러 발생 시 처리 거부
        } else {
            prom.resolve(token); // 정상 시 토큰과 함께 처리 승인
        }
    });
    // 처리가 끝나면 큐를 비웁니다.
    failedQueue = [];
};

/**
 * 브라우저 내장 fetch API를 덮어써서 인터셉터(가로채기) 역할을 수행합니다.
 */
window.fetch = async (...args) => {
    let [resource, config] = args;
    
    // 1. 기존 fetch 메서드를 사용하여 기본 요청부터 수행합니다.
    let response = await originalFetch(resource, config);

    const urlStr = typeof resource === 'string' ? resource : resource?.url || '';
    
    // 2. 만약 401(Unauthorized) 응답이 발생했고, 해당 요청이 로그인 및 토큰 갱신 관련 API가 아니라면 토큰 갱신을 시도합니다.
    if (response.status === 401 && !urlStr.includes('/auth/login') && !urlStr.includes('/auth/refresh') && !urlStr.includes('/auth/signup') && !urlStr.includes('/auth/check-email')) {
        const refreshToken = localStorage.getItem('refreshToken');
        
        // 리프레시 토큰이 로컬 스토리지에 아예 없다면 즉시 로그아웃 처리하고 로그인 페이지로 보냅니다.
        if (!refreshToken) {
            localStorage.clear();
            window.location.href = '/'; // 수정: /login 대신 로그인 루트 페이지(/)로 이동하도록 변경
            return response;
        }

        // 이미 다른 요청으로 인해 토큰 갱신 로직이 수행 중이라면...
        if (isRefreshing) {
            // 새 토큰이 발급될 때까지 프로미스(Promise)로 감싸서 큐에 대기시켰다가 재시도합니다.
            return new Promise((resolve, reject) => {
                failedQueue.push({ resolve, reject });
            }).then(token => {
                const newConfig = config ? { ...config } : {};
                // 새 토큰을 Authorization 헤더에 담아서 다시 요청합니다.
                newConfig.headers = {
                    ...(newConfig.headers || {}),
                    'Authorization': `Bearer ${token}`
                };
                return originalFetch(resource, newConfig);
            }).catch(err => {
                // 실패 시 원래의 에러 응답 객체 반환
                return response;
            });
        }

        // 갱신 시작 플래그 On
        isRefreshing = true;

        try {
            // 새 토큰 발급을 직접 요청합니다.
            const refreshResponse = await originalFetch(`${API_BASE_URL}/auth/refresh`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ refreshToken })
            });

            if (refreshResponse.ok) {
                // 토큰 갱신 성공 시 서버에서 내려준 토큰 정보를 획득합니다.
                const result = await refreshResponse.json();
                const newAccessToken = result.data.accessToken;
                const newRefreshToken = result.data.refreshToken;

                // 새로 발급된 토큰들을 로컬 스토리지에 업데이트합니다.
                localStorage.setItem('accessToken', newAccessToken);
                localStorage.setItem('refreshToken', newRefreshToken);

                // 대기하고 있던 큐(기존 실패했던 요청들)들의 처리를 위해 새 토큰을 전달합니다.
                processQueue(null, newAccessToken);

                // 현재 실패했던 요청에 대해서도 새 토큰을 헤더에 넣어서 다시 발송합니다.
                const newConfig = config ? { ...config } : {};
                newConfig.headers = {
                    ...(newConfig.headers || {}),
                    'Authorization': `Bearer ${newAccessToken}`
                };
                response = await originalFetch(resource, newConfig);
            } else {
                // 서버에서 리프레시 토큰이 만료되었거나 유효하지 않다고 알려준 경우
                // 큐에 대기중이던 요청들에게 에러를 전달하고 강제로 로그아웃 시킵니다.
                processQueue(new Error('Refresh token invalid'));
                localStorage.clear();
                window.location.href = '/';
            }
        } catch (error) {
            // 토큰 갱신 과정 중 네트워크 라우팅 문제나 서버 문제 등으로 실패 시
            processQueue(error);
            localStorage.clear();
            window.location.href = '/';
        } finally {
            // 모든 갱신 시도가 종료되면 진행 상태 플래그를 Off로 변경합니다.
            isRefreshing = false;
        }
    }

    // 최종적으로 응답(Response) 객체를 반환합니다.
    return response;
};
