package site.to_mato.user.service;

import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import site.to_mato.common.exception.BusinessException;
import site.to_mato.common.exception.ErrorCode;
import site.to_mato.user.dto.response.MyProfileResponse;
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

    public MyProfileResponse getMyProfile(Long userId) {
        User user = userRepository.findById(userId)
                .orElseThrow(() -> new BusinessException(ErrorCode.USER_NOT_FOUND));

        List<Long> skillIds = userSkillRepository.findAllByUser_Id(userId).stream()
                .map(userSkill -> userSkill.getSkill().getId())
                .toList();

        List<Long> companyIds = userDesiredCompanyRepository.findAllByUser_Id(userId).stream()
                .map(userCompany -> userCompany.getCompany().getId())
                .toList();

        return MyProfileResponse.builder()
                .email(user.getEmail())
                .nickname(user.getNickname())
                .githubUsername(user.getGithubUsername())
                .position(user.getPosition() != null ? user.getPosition().getId() : null)
                .companyIds(companyIds)
                .skillIds(skillIds)
                .build();
    }

    public UserProfileResponse getUserProfile(Long userId) {
        User user = userRepository.findById(userId)
                .orElseThrow(() -> new BusinessException(ErrorCode.USER_NOT_FOUND));

        List<Long> skillIds = userSkillRepository.findAllByUser_Id(userId).stream()
                .map(userSkill -> userSkill.getSkill().getId())
                .toList();

        List<Long> companyIds = userDesiredCompanyRepository.findAllByUser_Id(userId).stream()
                .map(userCompany -> userCompany.getCompany().getId())
                .toList();

        return UserProfileResponse.builder()
                .nickname(user.getNickname())
                .githubUsername(user.getGithubUsername())
                .position(user.getPosition() != null ? user.getPosition().getId() : null)
                .skillIds(skillIds)
                .companyIds(companyIds)
                .build();
    }
}