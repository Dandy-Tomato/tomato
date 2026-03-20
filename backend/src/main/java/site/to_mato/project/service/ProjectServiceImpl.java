package site.to_mato.project.service;

import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import site.to_mato.catalog.entity.Domain;
import site.to_mato.catalog.entity.Position;
import site.to_mato.catalog.repository.DomainRepository;
import site.to_mato.catalog.repository.PositionRepository;
import site.to_mato.catalog.repository.SkillRepository;
import site.to_mato.common.exception.BusinessException;
import site.to_mato.common.exception.ErrorCode;
import site.to_mato.common.security.CurrentUserProvider;
import site.to_mato.project.dto.ProjectRequestDto;
import site.to_mato.project.dto.ProjectResponseDto;
import site.to_mato.project.entity.*;
import site.to_mato.project.repository.*;
import site.to_mato.user.entity.User;
import site.to_mato.user.repository.UserRepository;
import site.to_mato.user.repository.UserSkillRepository;

import java.time.LocalDateTime;
import java.util.*;
import java.util.function.Function;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
@Transactional(readOnly = true)
public class ProjectServiceImpl implements ProjectService {

    private final CurrentUserProvider currentUserProvider;

    private final ProjectRepository projectRepository;
    private final ProjectMemberRepository projectMemberRepository;
    private final ProjectDomainRepository projectDomainRepository;
    private final ProjectSkillRepository projectSkillRepository;

    private final UserRepository userRepository;
    private final UserSkillRepository userSkillRepository;

    private final DomainRepository domainRepository;
    private final SkillRepository skillRepository;
    private final PositionRepository positionRepository;

    @Override
    @Transactional
    public ProjectResponseDto.CreateData createProject(ProjectRequestDto.Create request) {
        validateDates(request.startedAt(), request.dueAt());

        Long currentUserId = currentUserProvider.getCurrentUserId();
        User owner = getUserOrThrow(currentUserId);

        List<Domain> domains = getDomainsOrThrow(request.domainIds());

        Project project = Project.builder()
                .name(request.name())
                .description(request.description())
                .startedAt(request.startedAt())
                .dueAt(request.dueAt())
                .inviteCode(generateUniqueInviteCode())
                .topicState(false)
                .ownerId(currentUserId)
                .confirmedChildTopicId(null)
                .build();

        Project savedProject = projectRepository.save(project);

        ProjectMember ownerMember = ProjectMember.builder()
                .projectId(savedProject.getId())
                .userId(currentUserId)
                .projectRole(ProjectRole.OWNER)
                .build();
        projectMemberRepository.save(ownerMember);

        replaceProjectDomains(savedProject.getId(), domains);
        recalculateProjectSkills(savedProject.getId());

        return new ProjectResponseDto.CreateData(
                savedProject.getId(),
                savedProject.getName(),
                savedProject.getDescription(),
                savedProject.getStartedAt(),
                savedProject.getDueAt(),
                savedProject.getInviteCode(),
                savedProject.getTopicState(),
                new ProjectResponseDto.OwnerSummary(owner.getId(), owner.getNickname()),
                domains.stream()
                        .map(d -> new ProjectResponseDto.DomainItem(d.getId(), d.getName()))
                        .toList(),
                savedProject.getCreatedAt()
        );
    }

    @Override
    public List<ProjectResponseDto.MyProjectItem> getMyProjects() {
        Long currentUserId = currentUserProvider.getCurrentUserId();

        List<ProjectMember> memberships = new ArrayList<>(projectMemberRepository.findAllByUserId(currentUserId));
        memberships.sort(Comparator.comparing(ProjectMember::getCreatedAt).reversed());

        Set<Long> projectIds = memberships.stream()
                .map(ProjectMember::getProjectId)
                .collect(Collectors.toSet());

        Map<Long, Project> projectMap = projectRepository.findAllByIdInAndDeletedAtIsNull(projectIds)
                .stream()
                .collect(Collectors.toMap(Project::getId, Function.identity()));

        return memberships.stream()
                .map(member -> {
                    Project project = projectMap.get(member.getProjectId());
                    if (project == null) {
                        return null;
                    }
                    return new ProjectResponseDto.MyProjectItem(
                            project.getId(),
                            project.getName(),
                            project.getDescription(),
                            member.getProjectRole().name(),
                            Boolean.TRUE.equals(project.getTopicState()),
                            projectMemberRepository.countByProjectId(project.getId()),
                            project.getStartedAt(),
                            project.getDueAt(),
                            project.getCreatedAt()
                    );
                })
                .filter(Objects::nonNull)
                .toList();
    }

    @Override
    public ProjectResponseDto.DetailData getProjectDetail(Long projectId) {
        Long currentUserId = currentUserProvider.getCurrentUserId();

        Project project = getActiveProjectOrThrow(projectId);
        ensureProjectMember(projectId, currentUserId);

        User owner = getUserOrThrow(project.getOwnerId());

        List<ProjectResponseDto.DomainItem> domains = getDomainItems(projectId);
        List<ProjectResponseDto.ProjectSkillItem> skills = getProjectSkills(projectId);
        long memberCount = projectMemberRepository.countByProjectId(projectId);

        return new ProjectResponseDto.DetailData(
                project.getId(),
                project.getName(),
                project.getDescription(),
                project.getStartedAt(),
                project.getDueAt(),
                project.getInviteCode(),
                Boolean.TRUE.equals(project.getTopicState()),
                project.getConfirmedChildTopicId(),
                new ProjectResponseDto.OwnerSummary(owner.getId(), owner.getNickname()),
                domains,
                skills,
                memberCount,
                project.getCreatedAt(),
                project.getUpdatedAt()
        );
    }

    @Override
    @Transactional
    public ProjectResponseDto.UpdateData updateProject(Long projectId, ProjectRequestDto.Update request) {
        Long currentUserId = currentUserProvider.getCurrentUserId();

        Project project = getActiveProjectOrThrow(projectId);
        ensureProjectOwner(project, currentUserId);

        LocalDateTime nextStartedAt = request.startedAt() != null ? request.startedAt() : project.getStartedAt();
        LocalDateTime nextDueAt = request.dueAt() != null ? request.dueAt() : project.getDueAt();
        validateDates(nextStartedAt, nextDueAt);

        if (request.name() != null) {
            project.setName(request.name());
        }
        if (request.description() != null) {
            project.setDescription(request.description());
        }
        if (request.startedAt() != null) {
            project.setStartedAt(request.startedAt());
        }
        if (request.dueAt() != null) {
            project.setDueAt(request.dueAt());
        }

        List<ProjectResponseDto.DomainItem> updatedDomains = getDomainItems(projectId);
        if (request.domainIds() != null) {
            List<Domain> domains = getDomainsOrThrow(request.domainIds());
            replaceProjectDomains(projectId, domains);
            updatedDomains = domains.stream()
                    .map(d -> new ProjectResponseDto.DomainItem(d.getId(), d.getName()))
                    .toList();
        }

        Project saved = projectRepository.save(project);

        return new ProjectResponseDto.UpdateData(
                saved.getId(),
                saved.getName(),
                saved.getDescription(),
                saved.getStartedAt(),
                saved.getDueAt(),
                updatedDomains,
                saved.getUpdatedAt()
        );
    }

    @Override
    @Transactional
    public ProjectResponseDto.DeleteData deleteProject(Long projectId) {
        Long currentUserId = currentUserProvider.getCurrentUserId();

        Project project = getActiveProjectOrThrow(projectId);
        ensureProjectOwner(project, currentUserId);

        project.setDeletedAt(LocalDateTime.now());
        Project saved = projectRepository.save(project);

        return new ProjectResponseDto.DeleteData(saved.getId(), saved.getDeletedAt());
    }

    @Override
    @Transactional
    public ProjectResponseDto.TopicConfirmationData confirmProjectTopic(Long projectId, ProjectRequestDto.ConfirmTopic request) {
        Long currentUserId = currentUserProvider.getCurrentUserId();

        Project project = getActiveProjectOrThrow(projectId);
        ensureProjectOwner(project, currentUserId);

        project.setConfirmedChildTopicId(request.confirmedChildTopicId());
        project.setTopicState(true);

        Project saved = projectRepository.save(project);

        return new ProjectResponseDto.TopicConfirmationData(
                saved.getId(),
                saved.getTopicState(),
                saved.getConfirmedChildTopicId(),
                saved.getUpdatedAt()
        );
    }

    @Override
    @Transactional
    public ProjectResponseDto.TopicConfirmationData clearProjectTopic(Long projectId) {
        Long currentUserId = currentUserProvider.getCurrentUserId();

        Project project = getActiveProjectOrThrow(projectId);
        ensureProjectOwner(project, currentUserId);

        project.setConfirmedChildTopicId(null);
        project.setTopicState(false);

        Project saved = projectRepository.save(project);

        return new ProjectResponseDto.TopicConfirmationData(
                saved.getId(),
                saved.getTopicState(),
                saved.getConfirmedChildTopicId(),
                saved.getUpdatedAt()
        );
    }

    @Override
    public ProjectResponseDto.InviteLookupData lookupInviteCode(String inviteCode) {
        Long currentUserId = currentUserProvider.getCurrentUserId();

        Project project = projectRepository.findByInviteCodeAndDeletedAtIsNull(inviteCode)
                .orElseThrow(() -> new BusinessException(ErrorCode.INVALID_INVITE_CODE));

        User owner = getUserOrThrow(project.getOwnerId());
        boolean alreadyJoined = projectMemberRepository.existsByProjectIdAndUserId(project.getId(), currentUserId);

        return new ProjectResponseDto.InviteLookupData(
                project.getId(),
                project.getName(),
                owner.getNickname(),
                alreadyJoined
        );
    }

    @Override
    @Transactional
    public ProjectResponseDto.JoinData joinProject(ProjectRequestDto.Join request) {
        Long currentUserId = currentUserProvider.getCurrentUserId();

        Project project = projectRepository.findByInviteCodeAndDeletedAtIsNull(request.inviteCode())
                .orElseThrow(() -> new BusinessException(ErrorCode.INVALID_INVITE_CODE));

        if (projectMemberRepository.existsByProjectIdAndUserId(project.getId(), currentUserId)) {
            throw new BusinessException(ErrorCode.ALREADY_JOINED_PROJECT);
        }

        ProjectMember member = ProjectMember.builder()
                .projectId(project.getId())
                .userId(currentUserId)
                .projectRole(ProjectRole.MEMBER)
                .build();

        ProjectMember savedMember = projectMemberRepository.save(member);
        recalculateProjectSkills(project.getId());

        return new ProjectResponseDto.JoinData(
                project.getId(),
                project.getName(),
                savedMember.getProjectRole().name(),
                savedMember.getCreatedAt()
        );
    }

    @Override
    public List<ProjectResponseDto.ProjectMemberItem> getProjectMembers(Long projectId) {
        Long currentUserId = currentUserProvider.getCurrentUserId();
        ensureProjectMember(projectId, currentUserId);
        getActiveProjectOrThrow(projectId);

        List<ProjectMember> members = projectMemberRepository.findAllByProjectId(projectId);

        Set<Long> userIds = members.stream()
                .map(ProjectMember::getUserId)
                .collect(Collectors.toSet());

        Map<Long, User> userMap = userRepository.findAllById(userIds)
                .stream()
                .collect(Collectors.toMap(User::getId, Function.identity()));

        Set<Long> positionIds = userMap.values().stream()
                .map(User::getPositionId)
                .filter(Objects::nonNull)
                .collect(Collectors.toSet());

        Map<Long, Position> positionMap = positionRepository.findAllById(positionIds)
                .stream()
                .collect(Collectors.toMap(Position::getId, Function.identity()));

        return members.stream()
                .map(member -> {
                    User user = userMap.get(member.getUserId());
                    if (user == null) {
                        throw new BusinessException(ErrorCode.USER_NOT_FOUND);
                    }

                    Position position = user.getPositionId() == null ? null : positionMap.get(user.getPositionId());
                    ProjectResponseDto.PositionSummary positionSummary = position == null
                            ? null
                            : new ProjectResponseDto.PositionSummary(position.getId(), position.getName());

                    return new ProjectResponseDto.ProjectMemberItem(
                            member.getId(),
                            user.getId(),
                            user.getNickname(),
                            user.getGithubUsername(),
                            member.getProjectRole().name(),
                            positionSummary,
                            member.getCreatedAt()
                    );
                })
                .toList();
    }

    @Override
    @Transactional
    public ProjectResponseDto.LeaveData leaveProject(Long projectId) {
        Long currentUserId = currentUserProvider.getCurrentUserId();

        ProjectMember member = projectMemberRepository.findByProjectIdAndUserId(projectId, currentUserId)
                .orElseThrow(() -> new BusinessException(ErrorCode.PROJECT_MEMBER_NOT_FOUND));

        if (member.getProjectRole() == ProjectRole.OWNER) {
            throw new BusinessException(ErrorCode.OWNER_CANNOT_LEAVE);
        }

        projectMemberRepository.delete(member);
        recalculateProjectSkills(projectId);

        return new ProjectResponseDto.LeaveData(projectId, currentUserId, LocalDateTime.now());
    }

    @Override
    @Transactional
    public ProjectResponseDto.TransferOwnerData transferOwner(Long projectId, ProjectRequestDto.TransferOwner request) {
        Long currentUserId = currentUserProvider.getCurrentUserId();

        Project project = getActiveProjectOrThrow(projectId);
        ensureProjectOwner(project, currentUserId);

        ProjectMember currentOwnerMember = projectMemberRepository.findByProjectIdAndUserId(projectId, currentUserId)
                .orElseThrow(() -> new BusinessException(ErrorCode.PROJECT_MEMBER_NOT_FOUND));

        ProjectMember newOwnerMember = projectMemberRepository.findByProjectIdAndUserId(projectId, request.newOwnerUserId())
                .orElseThrow(() -> new BusinessException(ErrorCode.PROJECT_MEMBER_NOT_FOUND));

        project.setOwnerId(request.newOwnerUserId());
        projectRepository.save(project);

        currentOwnerMember.setProjectRole(ProjectRole.MEMBER);
        newOwnerMember.setProjectRole(ProjectRole.OWNER);
        projectMemberRepository.saveAll(List.of(currentOwnerMember, newOwnerMember));

        return new ProjectResponseDto.TransferOwnerData(
                projectId,
                currentUserId,
                request.newOwnerUserId(),
                project.getUpdatedAt()
        );
    }

    @Override
    public List<ProjectResponseDto.ProjectDomainItem> getProjectDomains(Long projectId) {
        Long currentUserId = currentUserProvider.getCurrentUserId();

        getActiveProjectOrThrow(projectId);
        ensureProjectMember(projectId, currentUserId);

        List<ProjectDomain> projectDomains = projectDomainRepository.findAllByProjectId(projectId);
        Set<Long> domainIds = projectDomains.stream()
                .map(ProjectDomain::getDomainId)
                .collect(Collectors.toSet());

        Map<Long, Domain> domainMap = domainRepository.findAllById(domainIds)
                .stream()
                .collect(Collectors.toMap(Domain::getId, Function.identity()));

        return projectDomains.stream()
                .map(pd -> {
                    Domain domain = domainMap.get(pd.getDomainId());
                    if (domain == null) {
                        throw new BusinessException(ErrorCode.DOMAIN_NOT_FOUND);
                    }
                    return new ProjectResponseDto.ProjectDomainItem(pd.getId(), domain.getId(), domain.getName());
                })
                .toList();
    }

    @Override
    public List<ProjectResponseDto.ProjectSkillItem> getProjectSkills(Long projectId) {
        Long currentUserId = currentUserProvider.getCurrentUserId();

        getActiveProjectOrThrow(projectId);
        ensureProjectMember(projectId, currentUserId);

        List<ProjectSkill> projectSkills = projectSkillRepository.findAllByProjectIdOrderByWeightDescIdAsc(projectId);
        Set<Long> skillIds = projectSkills.stream()
                .map(ProjectSkill::getSkillId)
                .collect(Collectors.toSet());

        Map<Long, Skill> skillMap = skillRepository.findAllById(skillIds)
                .stream()
                .collect(Collectors.toMap(Skill::getId, Function.identity()));

        return projectSkills.stream()
                .map(ps -> {
                    Skill skill = skillMap.get(ps.getSkillId());
                    if (skill == null) {
                        throw new BusinessException(ErrorCode.SKILL_NOT_FOUND);
                    }
                    return new ProjectResponseDto.ProjectSkillItem(
                            ps.getId(),
                            skill.getId(),
                            skill.getName(),
                            ps.getWeight().longValue()
                    );
                })
                .toList();
    }

    @Override
    @Transactional
    public void refreshProjectSkillsForUser(Long userId) {
        List<ProjectMember> memberships = projectMemberRepository.findAllByUserId(userId);
        Set<Long> projectIds = memberships.stream()
                .map(ProjectMember::getProjectId)
                .collect(Collectors.toSet());

        for (Long projectId : projectIds) {
            recalculateProjectSkills(projectId);
        }
    }

    private Project getActiveProjectOrThrow(Long projectId) {
        return projectRepository.findByIdAndDeletedAtIsNull(projectId)
                .orElseThrow(() -> new BusinessException(ErrorCode.PROJECT_NOT_FOUND));
    }

    private User getUserOrThrow(Long userId) {
        return userRepository.findById(userId)
                .orElseThrow(() -> new BusinessException(ErrorCode.USER_NOT_FOUND));
    }

    private void ensureProjectMember(Long projectId, Long userId) {
        if (!projectMemberRepository.existsByProjectIdAndUserId(projectId, userId)) {
            throw new BusinessException(ErrorCode.FORBIDDEN);
        }
    }

    private void ensureProjectOwner(Project project, Long userId) {
        if (!Objects.equals(project.getOwnerId(), userId)) {
            throw new BusinessException(ErrorCode.FORBIDDEN);
        }
    }

    private void validateDates(LocalDateTime startedAt, LocalDateTime dueAt) {
        if (startedAt != null && dueAt != null && startedAt.isAfter(dueAt)) {
            throw new BusinessException(ErrorCode.INVALID_REQUEST);
        }
    }

    private List<Domain> getDomainsOrThrow(List<Long> domainIds) {
        if (domainIds == null) {
            return List.of();
        }

        List<Long> distinctIds = domainIds.stream().distinct().toList();
        List<Domain> domains = domainRepository.findAllById(distinctIds);

        if (domains.size() != distinctIds.size()) {
            throw new BusinessException(ErrorCode.DOMAIN_NOT_FOUND);
        }

        return domains;
    }

    @Transactional
    protected void replaceProjectDomains(Long projectId, List<Domain> domains) {
        projectDomainRepository.deleteAllByProjectId(projectId);

        if (domains.isEmpty()) {
            return;
        }

        List<ProjectDomain> entities = domains.stream()
                .map(domain -> ProjectDomain.builder()
                        .projectId(projectId)
                        .domainId(domain.getId())
                        .weight(1.0d)
                        .build())
                .toList();

        projectDomainRepository.saveAll(entities);
    }

    @Transactional
    protected void recalculateProjectSkills(Long projectId) {
        projectSkillRepository.deleteAllByProjectId(projectId);

        List<UserSkillRepository.SkillCountView> aggregated = userSkillRepository.aggregateProjectSkills(projectId);
        if (aggregated.isEmpty()) {
            return;
        }

        List<ProjectSkill> entities = aggregated.stream()
                .map(row -> ProjectSkill.builder()
                        .projectId(projectId)
                        .skillId(row.getSkillId())
                        .weight(row.getSkillCount().doubleValue())
                        .build())
                .toList();

        projectSkillRepository.saveAll(entities);
    }

    private String generateUniqueInviteCode() {
        String chars = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789";
        Random random = new Random();

        while (true) {
            StringBuilder sb = new StringBuilder();
            for (int i = 0; i < 8; i++) {
                sb.append(chars.charAt(random.nextInt(chars.length())));
            }
            String code = sb.toString();

            if (!projectRepository.existsByInviteCode(code)) {
                return code;
            }
        }
    }

    private List<ProjectResponseDto.DomainItem> getDomainItems(Long projectId) {
        List<ProjectDomain> projectDomains = projectDomainRepository.findAllByProjectId(projectId);
        Set<Long> domainIds = projectDomains.stream()
                .map(ProjectDomain::getDomainId)
                .collect(Collectors.toSet());

        Map<Long, Domain> domainMap = domainRepository.findAllById(domainIds)
                .stream()
                .collect(Collectors.toMap(Domain::getId, Function.identity()));

        return projectDomains.stream()
                .map(pd -> {
                    Domain domain = domainMap.get(pd.getDomainId());
                    if (domain == null) {
                        throw new BusinessException(ErrorCode.DOMAIN_NOT_FOUND);
                    }
                    return new ProjectResponseDto.DomainItem(domain.getId(), domain.getName());
                })
                .toList();
    }
}