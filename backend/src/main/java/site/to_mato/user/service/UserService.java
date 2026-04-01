package site.to_mato.user.service;

import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import site.to_mato.common.exception.BusinessException;
import site.to_mato.common.exception.ErrorCode;
import site.to_mato.user.dto.response.DesiredCompanyResponse;
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
        User user = getUser(userId);
        return buildUserProfileResponse(user, true);
    }

    public UserProfileResponse getUserProfile(Long userId) {
        User user = getUser(userId);
        return buildUserProfileResponse(user, false);
    }

    private User getUser(Long userId) {
        return userRepository.findById(userId)
                .orElseThrow(() -> new BusinessException(ErrorCode.USER_NOT_FOUND));
    }

    private UserProfileResponse buildUserProfileResponse(User user, boolean includeEmail) {
        Long userId = user.getId();

        List<Long> skillIds = userSkillRepository.findAllByUser_Id(userId).stream()
                .map(userSkill -> userSkill.getSkill().getId())
                .toList();

        List<DesiredCompanyResponse> companies = userDesiredCompanyRepository.findAllByUser_Id(userId).stream()
                .map(userCompany -> new DesiredCompanyResponse(
                        userCompany.getCompany().getId(),
                        userCompany.getCompany().getName()
                ))
                .toList();

        return new UserProfileResponse(
                user.getId(),
                includeEmail ? user.getEmail() : null,
                user.getNickname(),
                user.getGithubUsername(),
                user.getPosition() != null ? user.getPosition().getId() : null,
                skillIds,
                companies
        );
    }
}
