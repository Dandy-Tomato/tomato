package site.to_mato.project.service;

import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import site.to_mato.catalog.entity.Domain;
import site.to_mato.catalog.entity.Skill;
import site.to_mato.company.repository.CompanySkillRepository;
import site.to_mato.project.entity.Project;
import site.to_mato.project.entity.ProjectDomain;
import site.to_mato.project.entity.ProjectSkill;
import site.to_mato.project.repository.ProjectDomainRepository;
import site.to_mato.project.repository.ProjectSkillRepository;
import site.to_mato.user.entity.User;
import site.to_mato.user.entity.UserSkill;
import site.to_mato.user.repository.UserDesiredCompanyRepository;
import site.to_mato.user.repository.UserSkillRepository;

import java.util.List;
import java.util.Objects;
import java.util.Optional;
import java.util.stream.Collectors;
import java.util.stream.Stream;

@Service
@RequiredArgsConstructor
public class ProjectProfileService {

    private static final double MEMBER_WEIGHT = 1.0;
    private static final double SELECTED_WEIGHT = 2.0;

    private final CompanySkillRepository companySkillRepository;
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
        for (Skill skill : getDistinctMemberSkills(userId)) {
            addMemberSkill(project, skill);
        }
    }

    private void removeUserSkills(Project project, Long userId) {
        for (Skill skill : getDistinctMemberSkills(userId)) {
            removeMemberSkill(project, skill.getId());
        }
    }

    private void addUserDomains(Project project, Long userId) {
        List<Domain> domains = userDesiredCompanyRepository.findDistinctDomainsByUserId(userId);

        for (Domain domain : domains) {
            addMemberDomain(project, domain);
        }
    }

    private void removeUserDomains(Project project, Long userId) {
        List<Domain> domains = userDesiredCompanyRepository.findDistinctDomainsByUserId(userId);

        for (Domain domain : domains) {
            removeMemberDomain(project, domain.getId());
        }
    }

    private List<Skill> getDistinctMemberSkills(Long userId) {
        List<Skill> userSkills = userSkillRepository.findAllByUser_Id(userId).stream()
                .map(UserSkill::getSkill)
                .filter(Objects::nonNull)
                .toList();

        List<Long> companyIds = userDesiredCompanyRepository.findDistinctCompanyIdsByUserId(userId);

        List<Skill> companySkills = companyIds.isEmpty()
                ? List.of()
                : companySkillRepository.findDistinctSkillsByCompanyIds(companyIds);

        return Stream.concat(userSkills.stream(), companySkills.stream())
                .collect(Collectors.toMap(
                        Skill::getId,
                        skill -> skill,
                        (a, b) -> a
                ))
                .values()
                .stream()
                .toList();
    }

    private void replaceSelectedSkills(Project project, List<Skill> selectedSkills) {
        List<ProjectSkill> projectSkills =
                projectSkillRepository.findAllByProject_Id(project.getId());

        for (ProjectSkill projectSkill : projectSkills) {
            removeSelectedSkill(projectSkill);
        }

        for (Skill skill : selectedSkills) {
            addSelectedSkill(project, skill);
        }
    }

    private void replaceSelectedDomains(Project project, List<Domain> selectedDomains) {
        List<ProjectDomain> projectDomains =
                projectDomainRepository.findAllByProject_Id(project.getId());

        for (ProjectDomain projectDomain : projectDomains) {
            removeSelectedDomain(projectDomain);
        }

        for (Domain domain : selectedDomains) {
            addSelectedDomain(project, domain);
        }
    }

    private void addMemberSkill(Project project, Skill skill) {
        Optional<ProjectSkill> optional =
                projectSkillRepository.findByProject_IdAndSkill_Id(project.getId(), skill.getId());

        if (optional.isPresent()) {
            optional.get().increaseWeight(MEMBER_WEIGHT);
            return;
        }

        projectSkillRepository.save(ProjectSkill.of(project, skill, MEMBER_WEIGHT));
    }

    private void removeMemberSkill(Project project, Long skillId) {
        projectSkillRepository.findByProject_IdAndSkill_Id(project.getId(), skillId)
                .ifPresent(projectSkill -> {
                    projectSkill.decreaseWeight(MEMBER_WEIGHT);

                    if (projectSkill.isWeightZeroOrNegative()) {
                        projectSkillRepository.delete(projectSkill);
                    }
                });
    }

    private void addSelectedSkill(Project project, Skill skill) {
        Optional<ProjectSkill> optional =
                projectSkillRepository.findByProject_IdAndSkill_Id(project.getId(), skill.getId());

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
                projectDomainRepository.findByProject_IdAndDomain_Id(project.getId(), domain.getId());

        if (optional.isPresent()) {
            optional.get().increaseWeight(MEMBER_WEIGHT);
            return;
        }

        projectDomainRepository.save(ProjectDomain.of(project, domain, MEMBER_WEIGHT));
    }

    private void removeMemberDomain(Project project, Long domainId) {
        projectDomainRepository.findByProject_IdAndDomain_Id(project.getId(), domainId)
                .ifPresent(projectDomain -> {
                    projectDomain.decreaseWeight(MEMBER_WEIGHT);

                    if (projectDomain.isWeightZeroOrNegative()) {
                        projectDomainRepository.delete(projectDomain);
                    }
                });
    }

    private void addSelectedDomain(Project project, Domain domain) {
        Optional<ProjectDomain> optional =
                projectDomainRepository.findByProject_IdAndDomain_Id(project.getId(), domain.getId());

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
