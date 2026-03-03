package site.to_mato.auth.service;

import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import site.to_mato.auth.dto.response.TokenResponse;
import site.to_mato.common.exception.ErrorCode;
import site.to_mato.common.exception.BusinessException;
import site.to_mato.common.response.ApiResponse;
import site.to_mato.common.security.jwt.JwtTokenProvider;
import site.to_mato.user.entity.User;
import site.to_mato.user.repository.UserRepository;

@Service
@RequiredArgsConstructor
public class AuthService {

    private final JwtTokenProvider jwtTokenProvider;
    private final RefreshTokenStore refreshTokenStore;
    private final UserRepository userRepository;

    public TokenResponse refresh(String oldRefreshToken) {

        if (oldRefreshToken == null || oldRefreshToken.isBlank()
                || !jwtTokenProvider.validateToken(oldRefreshToken)) {
            throw new BusinessException(ErrorCode.REFRESH_TOKEN_INVALID);
        }

        Long userId = refreshTokenStore.findUserId(oldRefreshToken);
        if (userId == null) {
            throw new BusinessException(ErrorCode.REFRESH_TOKEN_REVOKED);
        }

        User user = userRepository.findById(userId)
                .orElseThrow(() -> new BusinessException(ErrorCode.USER_NOT_FOUND));

        String role = user.getRole().name();

        String newAccess = jwtTokenProvider.createAccessToken(userId, role);
        String newRefresh = jwtTokenProvider.createRefreshToken(userId);

        refreshTokenStore.rotate(oldRefreshToken, newRefresh, userId);

        return TokenResponse.builder()
                .accessToken(newAccess)
                .refreshToken(newRefresh)
                .build();
    }
}