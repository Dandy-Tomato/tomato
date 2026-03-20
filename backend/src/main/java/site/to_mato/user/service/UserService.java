package site.to_mato.user.service;

import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import site.to_mato.common.exception.BusinessException;
import site.to_mato.common.exception.ErrorCode;
import site.to_mato.user.dto.response.UserProfileResponse;
import site.to_mato.user.entity.User;
import site.to_mato.user.repository.UserDesiredCompanyRepository;
import site.to_mato.user.repository.UserRepository;
import site.to_mato.user.repository.UserSkillRepository;

import java.util.List;

@Service
@RequiredArgsConstructor
@Transactional(readOnly = true)
public class UserService {

    private final UserRepository userRepository;
    private final UserSkillRepository userSkillRepository;
    private final UserDesiredCompanyRepository userDesiredCompanyRepository;

    public UserProfileResponse getMyProfile(Long userId) {
        User user = userRepository.findByIdAndDeletedAtIsNull(userId)
                .orElseThrow(() -> new BusinessException(ErrorCode.USER_NOT_FOUND));

        List<Long> skillIds = userSkillRepository.findAllByUser_IdAndUser_DeletedAtIsNull(userId).stream()
                .map(userSkill -> userSkill.getSkill().getId())
                .toList();

        List<Long> companyIds = userDesiredCompanyRepository.findAllByUser_IdAndUser_DeletedAtIsNull(userId).stream()
                .map(userCompany -> userCompany.getCompany().getId())
                .toList();

        return UserProfileResponse.of(
                user.getEmail(),
                user.getNickname(),
                user.getGithubUsername(),
                user.getPosition() != null ? user.getPosition().getId() : null,
                skillIds,
                companyIds
        );
    }

    public UserProfileResponse getUserProfile(Long userId) {
        User user = userRepository.findByIdAndDeletedAtIsNull(userId)
                .orElseThrow(() -> new BusinessException(ErrorCode.USER_NOT_FOUND));

        List<Long> skillIds = userSkillRepository.findAllByUser_IdAndUser_DeletedAtIsNull(userId).stream()
                .map(userSkill -> userSkill.getSkill().getId())
                .toList();

        List<Long> companyIds = userDesiredCompanyRepository.findAllByUser_IdAndUser_DeletedAtIsNull(userId).stream()
                .map(userCompany -> userCompany.getCompany().getId())
                .toList();

        return UserProfileResponse.of(
                null,
                user.getNickname(),
                user.getGithubUsername(),
                user.getPosition() != null ? user.getPosition().getId() : null,
                skillIds,
                companyIds
        );
    }
}
