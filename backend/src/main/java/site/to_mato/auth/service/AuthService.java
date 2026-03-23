package site.to_mato.auth.service;

import lombok.RequiredArgsConstructor;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import site.to_mato.auth.dto.request.LoginRequest;
import site.to_mato.auth.dto.request.OnboardingRequest;
import site.to_mato.auth.dto.request.SignUpRequest;
import site.to_mato.auth.dto.response.TokenResponse;
import site.to_mato.catalog.entity.Position;
import site.to_mato.catalog.entity.Skill;
import site.to_mato.catalog.repository.PositionRepository;
import site.to_mato.catalog.repository.SkillRepository;
import site.to_mato.common.exception.BusinessException;
import site.to_mato.common.exception.ErrorCode;
import site.to_mato.common.security.jwt.JwtTokenProvider;
import site.to_mato.company.entity.Company;
import site.to_mato.company.repository.CompanyRepository;
import site.to_mato.user.entity.User;
import site.to_mato.user.entity.UserDesiredCompany;
import site.to_mato.user.entity.UserSkill;
import site.to_mato.user.repository.UserDesiredCompanyRepository;
import site.to_mato.user.repository.UserRepository;
import site.to_mato.user.repository.UserSkillRepository;

import java.util.List;

@Service
@RequiredArgsConstructor
public class AuthService {

    private final UserRepository userRepository;
    private final SkillRepository skillRepository;
    private final CompanyRepository companyRepository;
    private final PositionRepository positionRepository;
    private final UserSkillRepository userSkillRepository;
    private final UserDesiredCompanyRepository userDesiredCompanyRepository;

    private final JwtTokenProvider jwtTokenProvider;
    private final RefreshTokenStore refreshTokenStore;
    private final PasswordEncoder passwordEncoder;

    public boolean isEmailAvailable(String email) {
        return !userRepository.existsByEmail(email);
    }

    @Transactional
    public void signup(SignUpRequest req) {
        if (userRepository.existsByEmail(req.email())) {
            throw new BusinessException(ErrorCode.DUPLICATE_USER);
        }

        String encodedPassword = passwordEncoder.encode(req.password());

        User user = User.createLocal(req.email(), encodedPassword);
        userRepository.save(user);
    }

    @Transactional
    public void updateProfile(Long userId, OnboardingRequest req) {
        User user = userRepository.findByIdAndDeletedAtIsNull(userId)
                .orElseThrow(() -> new BusinessException(ErrorCode.USER_NOT_FOUND));

        Position position = null;
        if (req.positionId() != null) {
            position = positionRepository.findById(req.positionId())
                    .orElseThrow(() -> new BusinessException(ErrorCode.POSITION_NOT_FOUND));
        }

        user.updateProfile(
                req.nickname(),
                req.githubUsername(),
                position
        );

        userDesiredCompanyRepository.deleteAllByUser(user);
        userDesiredCompanyRepository.flush();

        userSkillRepository.deleteAllByUser(user);
        userSkillRepository.flush();

        if (req.companyIds() != null && !req.companyIds().isEmpty()) {
            saveUserDesiredCompanies(user, req.companyIds());
        }

        if (req.skillIds() != null && !req.skillIds().isEmpty()) {
            saveUserSkills(user, req.skillIds());
        }
    }

    public TokenResponse login(LoginRequest req) {
        User user = userRepository.findByEmailAndDeletedAtIsNull(req.email())
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

        return TokenResponse.of(userId, access, refresh);
    }

    public TokenResponse refresh(String oldRefreshToken) {
        if (oldRefreshToken == null
                || oldRefreshToken.isBlank()
                || !jwtTokenProvider.validateToken(oldRefreshToken)) {
            throw new BusinessException(ErrorCode.REFRESH_TOKEN_INVALID);
        }

        Long userId = refreshTokenStore.findUserId(oldRefreshToken);
        if (userId == null) {
            throw new BusinessException(ErrorCode.REFRESH_TOKEN_REVOKED);
        }

        User user = userRepository.findByIdAndDeletedAtIsNull(userId)
                .orElseThrow(() -> new BusinessException(ErrorCode.USER_NOT_FOUND));

        String role = user.getRole().name();

        String newAccess = jwtTokenProvider.createAccessToken(userId, role);
        String newRefresh = jwtTokenProvider.createRefreshToken(userId);

        refreshTokenStore.rotate(oldRefreshToken, newRefresh, userId);

        return TokenResponse.of(userId, newAccess, newRefresh);
    }

    public void logout(String refreshToken) {
        if (refreshToken == null || refreshToken.isBlank()) return;
        refreshTokenStore.delete(refreshToken);
    }

    @Transactional
    public void signout(Long userId, String refreshToken) {
        User user = userRepository.findByIdAndDeletedAtIsNull(userId)
                .orElseThrow(() -> new BusinessException(ErrorCode.USER_NOT_FOUND));

        if (refreshToken != null && !refreshToken.isBlank()) {
            refreshTokenStore.delete(refreshToken);
        }

        user.softDelete();
    }

    private void saveUserDesiredCompanies(User user, List<Long> companyIds) {
        if (companyIds == null || companyIds.isEmpty()) {
            return;
        }

        List<Long> distinctCompanyIds = companyIds.stream()
                .distinct()
                .toList();

        List<Company> companies = companyRepository.findAllById(distinctCompanyIds);

        if (companies.size() != distinctCompanyIds.size()) {
            throw new BusinessException(ErrorCode.COMPANY_NOT_FOUND);
        }

        List<UserDesiredCompany> userDesiredCompanies = companies.stream()
                .map(company -> UserDesiredCompany.of(user, company))
                .toList();

        userDesiredCompanyRepository.saveAll(userDesiredCompanies);
    }

    private void saveUserSkills(User user, List<Long> skillIds) {
        if (skillIds == null || skillIds.isEmpty()) {
            return;
        }

        List<Long> distinctSkillIds = skillIds.stream()
                .distinct()
                .toList();

        List<Skill> skills = skillRepository.findAllById(distinctSkillIds);

        if (skills.size() != distinctSkillIds.size()) {
            throw new BusinessException(ErrorCode.SKILL_NOT_FOUND);
        }

        List<UserSkill> userSkills = skills.stream()
                .map(skill -> UserSkill.of(user, skill))
                .toList();

        userSkillRepository.saveAll(userSkills);
    }
}
