package site.to_mato.project.service;

import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import site.to_mato.catalog.entity.Domain;
import site.to_mato.catalog.entity.Skill;
import site.to_mato.company.entity.Company;
import site.to_mato.project.entity.Project;
import site.to_mato.project.entity.ProjectDomain;
import site.to_mato.project.entity.ProjectSkill;
import site.to_mato.project.repository.ProjectDomainRepository;
import site.to_mato.project.repository.ProjectSkillRepository;
import site.to_mato.user.entity.User;
import site.to_mato.user.entity.UserDesiredCompany;
import site.to_mato.user.entity.UserSkill;
import site.to_mato.user.repository.UserDesiredCompanyRepository;
import site.to_mato.user.repository.UserSkillRepository;

import java.util.List;
import java.util.Objects;
import java.util.Optional;

@Service
@RequiredArgsConstructor
public class ProjectProfileService {

    private static final double MEMBER_WEIGHT = 1.0;
    private static final double SELECTED_WEIGHT = 3.0;

    private final ProjectSkillRepository projectSkillRepository;
    private final ProjectDomainRepository projectDomainRepository;
    private final UserSkillRepository userSkillRepository;
    private final UserDesiredCompanyRepository userDesiredCompanyRepository;

    @Transactional
    public void addMemberProfile(Project project, User user) {
        addUserSkills(project, user.getId());
        addUserDomains(project, user.getId());
    }

    @Transactional
    public void removeMemberProfile(Project project, User user) {
        removeUserSkills(project, user.getId());
        removeUserDomains(project, user.getId());
    }

    @Transactional
    public void addSelectedProfile(Project project, List<Skill> selectedSkills, List<Domain> selectedDomains) {
        for (Skill skill : selectedSkills) {
            addSelectedSkill(project, skill);
        }

        for (Domain domain : selectedDomains) {
            addSelectedDomain(project, domain);
        }
    }

    @Transactional
    public void replaceSelectedProfile(Project project, List<Skill> selectedSkills, List<Domain> selectedDomains) {
        replaceSelectedSkills(project, selectedSkills);
        replaceSelectedDomains(project, selectedDomains);
    }

    private void addUserSkills(Project project, Long userId) {
        List<UserSkill> userSkills = userSkillRepository.findAllByUser_IdAndUser_DeletedAtIsNull(userId);

        for (UserSkill userSkill : userSkills) {
            Skill skill = userSkill.getSkill();
            if (skill == null) {
                continue;
            }
            addMemberSkill(project, skill);
        }
    }

    private void removeUserSkills(Project project, Long userId) {
        List<UserSkill> userSkills = userSkillRepository.findAllByUser_IdAndUser_DeletedAtIsNull(userId);

        for (UserSkill userSkill : userSkills) {
            Skill skill = userSkill.getSkill();
            if (skill == null) {
                continue;
            }
            removeMemberSkill(project, skill.getId());
        }
    }

    private void addUserDomains(Project project, Long userId) {
        List<UserDesiredCompany> userDesiredCompanies =
                userDesiredCompanyRepository.findAllByUser_IdAndUser_DeletedAtIsNull(userId);

        List<Domain> domains = userDesiredCompanies.stream()
                .map(UserDesiredCompany::getCompany)
                .filter(Objects::nonNull)
                .map(Company::getDomain)
                .filter(Objects::nonNull)
                .distinct()
                .toList();

        for (Domain domain : domains) {
            addMemberDomain(project, domain);
        }
    }

    private void removeUserDomains(Project project, Long userId) {
        List<UserDesiredCompany> userDesiredCompanies =
                userDesiredCompanyRepository.findAllByUser_IdAndUser_DeletedAtIsNull(userId);

        List<Domain> domains = userDesiredCompanies.stream()
                .map(UserDesiredCompany::getCompany)
                .filter(Objects::nonNull)
                .map(Company::getDomain)
                .filter(Objects::nonNull)
                .distinct()
                .toList();

        for (Domain domain : domains) {
            removeMemberDomain(project, domain.getId());
        }
    }

    private void replaceSelectedSkills(Project project, List<Skill> selectedSkills) {
        List<ProjectSkill> projectSkills =
                projectSkillRepository.findAllByProjectIdAndProjectDeletedAtIsNull(project.getId());

        for (ProjectSkill projectSkill : projectSkills) {
            removeSelectedSkill(projectSkill);
        }

        for (Skill skill : selectedSkills) {
            addSelectedSkill(project, skill);
        }
    }

    private void replaceSelectedDomains(Project project, List<Domain> selectedDomains) {
        List<ProjectDomain> projectDomains =
                projectDomainRepository.findAllByProjectIdAndProjectDeletedAtIsNull(project.getId());

        for (ProjectDomain projectDomain : projectDomains) {
            removeSelectedDomain(projectDomain);
        }

        for (Domain domain : selectedDomains) {
            addSelectedDomain(project, domain);
        }
    }

    private void addMemberSkill(Project project, Skill skill) {
        Optional<ProjectSkill> optional =
                projectSkillRepository.findByProjectIdAndSkillIdAndProjectDeletedAtIsNull(project.getId(), skill.getId());

        if (optional.isPresent()) {
            optional.get().increaseWeight(MEMBER_WEIGHT);
            return;
        }

        projectSkillRepository.save(ProjectSkill.of(project, skill, MEMBER_WEIGHT));
    }

    private void removeMemberSkill(Project project, Long skillId) {
        projectSkillRepository.findByProjectIdAndSkillIdAndProjectDeletedAtIsNull(project.getId(), skillId)
                .ifPresent(projectSkill -> {
                    projectSkill.decreaseWeight(MEMBER_WEIGHT);

                    if (projectSkill.isWeightZeroOrNegative()) {
                        projectSkillRepository.delete(projectSkill);
                    }
                });
    }

    private void addSelectedSkill(Project project, Skill skill) {
        Optional<ProjectSkill> optional =
                projectSkillRepository.findByProjectIdAndSkillIdAndProjectDeletedAtIsNull(project.getId(), skill.getId());

        if (optional.isPresent()) {
            optional.get().increaseWeight(SELECTED_WEIGHT);
            return;
        }

        projectSkillRepository.save(ProjectSkill.of(project, skill, SELECTED_WEIGHT));
    }

    private void removeSelectedSkill(ProjectSkill projectSkill) {
        projectSkill.decreaseWeight(SELECTED_WEIGHT);

        if (projectSkill.isWeightZeroOrNegative()) {
            projectSkillRepository.delete(projectSkill);
        }
    }

    private void addMemberDomain(Project project, Domain domain) {
        Optional<ProjectDomain> optional =
                projectDomainRepository.findByProjectIdAndDomainIdAndProjectDeletedAtIsNull(project.getId(), domain.getId());

        if (optional.isPresent()) {
            optional.get().increaseWeight(MEMBER_WEIGHT);
            return;
        }

        projectDomainRepository.save(ProjectDomain.of(project, domain, MEMBER_WEIGHT));
    }

    private void removeMemberDomain(Project project, Long domainId) {
        projectDomainRepository.findByProjectIdAndDomainIdAndProjectDeletedAtIsNull(project.getId(), domainId)
                .ifPresent(projectDomain -> {
                    projectDomain.decreaseWeight(MEMBER_WEIGHT);

                    if (projectDomain.isWeightZeroOrNegative()) {
                        projectDomainRepository.delete(projectDomain);
                    }
                });
    }

    private void addSelectedDomain(Project project, Domain domain) {
        Optional<ProjectDomain> optional =
                projectDomainRepository.findByProjectIdAndDomainIdAndProjectDeletedAtIsNull(project.getId(), domain.getId());

        if (optional.isPresent()) {
            optional.get().increaseWeight(SELECTED_WEIGHT);
            return;
        }

        projectDomainRepository.save(ProjectDomain.of(project, domain, SELECTED_WEIGHT));
    }

    private void removeSelectedDomain(ProjectDomain projectDomain) {
        projectDomain.decreaseWeight(SELECTED_WEIGHT);

        if (projectDomain.isWeightZeroOrNegative()) {
            projectDomainRepository.delete(projectDomain);
        }
    }
}
