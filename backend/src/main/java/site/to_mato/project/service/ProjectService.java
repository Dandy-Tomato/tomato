package site.to_mato.project.service;

import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import site.to_mato.catalog.entity.Domain;
import site.to_mato.catalog.entity.Skill;
import site.to_mato.catalog.repository.DomainRepository;
import site.to_mato.catalog.repository.SkillRepository;
import site.to_mato.common.exception.BusinessException;
import site.to_mato.common.exception.ErrorCode;
import site.to_mato.project.dto.request.CreateProjectRequest;
import site.to_mato.project.dto.response.CreateProjectResponse;
import site.to_mato.project.entity.Project;
import site.to_mato.project.entity.ProjectMember;
import site.to_mato.project.repository.ProjectMemberRepository;
import site.to_mato.project.repository.ProjectRepository;
import site.to_mato.user.entity.User;
import site.to_mato.user.repository.UserRepository;

import java.security.SecureRandom;
import java.util.Collections;
import java.util.List;
import java.util.Objects;
import java.util.Optional;

@Service
@RequiredArgsConstructor
public class ProjectService {

    private final ProjectRepository projectRepository;
    private final ProjectMemberRepository projectMemberRepository;

    private final UserRepository userRepository;
    private final SkillRepository skillRepository;
    private final DomainRepository domainRepository;

    private final ProjectProfileService projectProfileService;

    @Transactional
    public CreateProjectResponse createProject(Long userId, CreateProjectRequest request) {
        if (request.dueAt().isBefore(request.startedAt())) {
            throw new BusinessException(ErrorCode.INVALID_PROJECT_DATE_RANGE);
        }

        User owner = userRepository.findByIdAndDeletedAtIsNull(userId)
                .orElseThrow(() -> new BusinessException(ErrorCode.USER_NOT_FOUND));
        List<Skill> selectedSkills = getSelectedSkills(request.techSkillIds());
        List<Domain> selectedDomains = getSelectedDomains(request.domainIds());

        Project project = Project.create(
                owner,
                request.name(),
                request.description(),
                request.startedAt(),
                request.dueAt(),
                generateInviteCode()
        );

        projectRepository.save(project);
        projectMemberRepository.save(ProjectMember.ofOwner(project, owner));

        projectProfileService.addMemberProfile(project, owner);
        projectProfileService.addSelectedProfile(project, selectedSkills, selectedDomains);

        return CreateProjectResponse.of(project.getId());
    }

    private List<Skill> getSelectedSkills(List<Long> skillIds) {
        List<Long> ids = Optional.ofNullable(skillIds)
                .orElse(Collections.emptyList())
                .stream()
                .filter(Objects::nonNull)
                .distinct()
                .toList();

        List<Skill> skills = skillRepository.findAllById(ids);
        if (skills.size() != ids.size()) {
            throw new BusinessException(ErrorCode.SKILL_NOT_FOUND);
        }

        return skills;
    }

    private List<Domain> getSelectedDomains(List<Long> domainIds) {
        List<Long> ids = Optional.ofNullable(domainIds)
                .orElse(Collections.emptyList())
                .stream()
                .filter(Objects::nonNull)
                .distinct()
                .toList();

        List<Domain> domains = domainRepository.findAllById(ids);
        if (domains.size() != ids.size()) {
            throw new BusinessException(ErrorCode.DOMAIN_NOT_FOUND);
        }

        return domains;
    }

    private String generateInviteCode() {
        String chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789";
        SecureRandom random = new SecureRandom();

        String code;
        do {
            StringBuilder sb = new StringBuilder(8);
            for (int i = 0; i < 8; i++) {
                sb.append(chars.charAt(random.nextInt(chars.length())));
            }
            code = sb.toString();
        } while (projectRepository.existsByInviteCodeAndDeletedAtIsNull(code));

        return code;
    }
}
