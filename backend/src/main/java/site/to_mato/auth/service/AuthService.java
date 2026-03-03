package site.to_mato.auth.service;

import lombok.RequiredArgsConstructor;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import site.to_mato.auth.dto.request.LoginRequest;
import site.to_mato.auth.dto.request.SignUpRequest;
import site.to_mato.auth.dto.response.TokenResponse;
import site.to_mato.common.exception.ErrorCode;
import site.to_mato.common.exception.BusinessException;
import site.to_mato.common.security.jwt.JwtTokenProvider;
import site.to_mato.user.entity.User;
import site.to_mato.user.repository.UserRepository;

@Service
@RequiredArgsConstructor
public class AuthService {

    private final JwtTokenProvider jwtTokenProvider;
    private final RefreshTokenStore refreshTokenStore;
    private final UserRepository userRepository;

    private final PasswordEncoder passwordEncoder;

    public void signup(SignUpRequest req) {
        if (userRepository.existsByEmail(req.email())) {
            throw new BusinessException(ErrorCode.DUPLICATE_USER);
        }

        String encoded = passwordEncoder.encode(req.password());

        User user = User.createLocal(req.email(), encoded, req.nickname());
        userRepository.save(user);
    }

    public TokenResponse login(LoginRequest req) {
        User user = userRepository.findByEmail(req.email())
                .orElseThrow(() -> new BusinessException(ErrorCode.INVALID_CREDENTIALS));

        if (user.getPassword() == null) {
            throw new BusinessException(ErrorCode.OAUTH_ONLY_ACCOUNT);
        }

        if (!passwordEncoder.matches(req.password(), user.getPassword())) {
            throw new BusinessException(ErrorCode.INVALID_CREDENTIALS);
        }

        Long userId = user.getId();
        String role = user.getRole().name();

        String access = jwtTokenProvider.createAccessToken(userId, role);
        String refresh = jwtTokenProvider.createRefreshToken(userId);

        refreshTokenStore.save(refresh, userId);

        return TokenResponse.builder()
                .accessToken(access)
                .refreshToken(refresh)
                .build();
    }

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

    public void logout(String refreshToken) {
        if (refreshToken == null || refreshToken.isBlank()) return;
        refreshTokenStore.delete(refreshToken);
    }
}