package site.to_mato.common.security.oauth;

import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import lombok.RequiredArgsConstructor;
import org.springframework.http.MediaType;
import org.springframework.security.core.Authentication;
import org.springframework.security.web.authentication.SimpleUrlAuthenticationSuccessHandler;
import org.springframework.stereotype.Component;
import site.to_mato.auth.service.RefreshTokenStore;
import site.to_mato.common.security.jwt.JwtProperties;
import site.to_mato.common.security.jwt.JwtTokenProvider;

import java.io.IOException;
import java.net.URLEncoder;
import java.nio.charset.StandardCharsets;

@Component
@RequiredArgsConstructor
public class CustomOAuth2SuccessHandler extends SimpleUrlAuthenticationSuccessHandler {

    private final JwtProperties jwtProperties;
    private final JwtTokenProvider jwtTokenProvider;
    private final RefreshTokenStore refreshTokenStore;

    @Override
    public void onAuthenticationSuccess(
            HttpServletRequest request,
            HttpServletResponse response,
            Authentication authentication
    ) throws IOException, ServletException {

        CustomOAuth2User principal = (CustomOAuth2User) authentication.getPrincipal();

        String access = jwtTokenProvider.createAccessToken(principal.userId(), principal.role());
        String refresh = jwtTokenProvider.createRefreshToken(principal.userId());

        refreshTokenStore.save(refresh, principal.userId());

        response.setCharacterEncoding(StandardCharsets.UTF_8.name());
        response.setContentType(MediaType.APPLICATION_JSON_VALUE);

        String redirectUrl = jwtProperties.frontCallbackUrl()
                + "#accessToken=" + URLEncoder.encode(access, StandardCharsets.UTF_8)
                + "&refreshToken=" + URLEncoder.encode(refresh, StandardCharsets.UTF_8);

        if (!principal.isOnboarding()) {
            redirectUrl += "&isOnboarding=false";
        }
        getRedirectStrategy().sendRedirect(request, response, redirectUrl);
    }
}
