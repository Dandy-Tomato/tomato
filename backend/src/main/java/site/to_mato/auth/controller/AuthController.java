package site.to_mato.auth.controller;

import jakarta.validation.Valid;
import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;
import lombok.RequiredArgsConstructor;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.*;
import site.to_mato.auth.dto.request.LoginRequest;
import site.to_mato.auth.dto.request.OnboardingRequest;
import site.to_mato.auth.dto.request.RefreshRequest;
import site.to_mato.auth.dto.request.SignUpRequest;
import site.to_mato.auth.dto.response.EmailCheckResponse;
import site.to_mato.auth.dto.response.TokenResponse;
import site.to_mato.auth.service.AuthService;
import site.to_mato.common.response.ApiResponse;

@Validated
@RestController
@RequiredArgsConstructor
@RequestMapping("/auth")
public class AuthController {

    private final AuthService authService;

    @GetMapping("/check-email")
    public ApiResponse<EmailCheckResponse> checkEmail(
            @RequestParam @Email @NotBlank String email
    ) {
        boolean available = authService.isEmailAvailable(email);
        return ApiResponse.ok(EmailCheckResponse.of(available));
    }

    @PostMapping("/signup")
    public ApiResponse<Void> signup(@RequestBody @Valid SignUpRequest req) {
        authService.signup(req);
        return ApiResponse.ok(null);
    }

    @PostMapping("/onboarding")
    public ApiResponse<Void> onboarding(
            @AuthenticationPrincipal Long userId,
            @RequestBody @Valid OnboardingRequest req
    ) {
        authService.updateProfile(userId, req);
        return ApiResponse.ok(null);
    }

    @PostMapping("/login")
    public ApiResponse<TokenResponse> login(@RequestBody @Valid LoginRequest req) {
        return ApiResponse.ok(authService.login(req));
    }

    @PostMapping("/refresh")
    public ApiResponse<TokenResponse> refresh(@RequestBody @Valid RefreshRequest req) {
        return ApiResponse.ok(authService.refresh(req.refreshToken()));
    }

    @PostMapping("/logout")
    public ApiResponse<Void> logout(@RequestBody @Valid RefreshRequest req) {
        authService.logout(req.refreshToken());
        return ApiResponse.ok(null);
    }

    @DeleteMapping("/signout")
    public ApiResponse<Void> signout(
            @AuthenticationPrincipal Long userId,
            @RequestBody @Valid RefreshRequest req
    ) {
        authService.signout(userId, req.refreshToken());
        return ApiResponse.ok(null);
    }
}
