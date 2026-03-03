package site.to_mato.auth.controller;

import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;
import site.to_mato.auth.dto.request.LoginRequest;
import site.to_mato.auth.dto.request.RefreshRequest;
import site.to_mato.auth.dto.request.SignUpRequest;
import site.to_mato.auth.dto.response.TokenResponse;
import site.to_mato.auth.service.AuthService;
import site.to_mato.common.response.ApiResponse;

@RestController
@RequiredArgsConstructor
@RequestMapping("/auth")
public class AuthController {

    private final AuthService authService;

    @PostMapping("/signup")
    public ApiResponse<Void> signup(@RequestBody @Valid SignUpRequest req) {
        authService.signup(req);
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
}