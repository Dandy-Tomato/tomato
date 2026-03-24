package site.to_mato.project.service;

import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import site.to_mato.common.exception.BusinessException;
import site.to_mato.common.exception.ErrorCode;
import site.to_mato.project.dto.response.MyProjectSummaryResponse;
import site.to_mato.project.dto.response.ProjectDetailResponse;
import site.to_mato.project.dto.response.ProjectMemberResponse;
import site.to_mato.project.dto.response.ProjectOwnerResponse;
import site.to_mato.project.entity.Project;
import site.to_mato.project.entity.ProjectMember;
import site.to_mato.project.repository.ProjectDomainRepository;
import site.to_mato.project.repository.ProjectMemberRepository;
import site.to_mato.project.repository.ProjectRepository;
import site.to_mato.user.entity.User;
import site.to_mato.user.repository.UserRepository;

import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class ProjectQueryService {

    private final UserRepository userRepository;
    private final ProjectRepository projectRepository;
    private final ProjectMemberRepository projectMemberRepository;
    private final ProjectDomainRepository projectDomainRepository;

    @Transactional(readOnly = true)
    public Page<MyProjectSummaryResponse> getMyProjects(Long userId, int page, int size) {
        validateUserExists(userId);

        PageRequest pageRequest = PageRequest.of(page, size);

        Page<ProjectMember> projectMembers =
                projectMemberRepository.findAllByUser_Id(
                        userId,
                        pageRequest
                );

        List<Long> projectIds = projectMembers.getContent().stream()
                .map(pm -> pm.getProject().getId())
                .distinct()
                .toList();

        Map<Long, Long> memberCountMap = projectIds.isEmpty()
                ? Map.of()
                : projectMemberRepository.countMembersByProjectIds(projectIds).stream()
                .collect(Collectors.toMap(
                        row -> (Long) row[0],
                        row -> (Long) row[1]
                ));

        return projectMembers.map(projectMember -> {
            Project project = projectMember.getProject();

            long memberCount = memberCountMap.getOrDefault(project.getId(), 0L);

            return MyProjectSummaryResponse.of(
                    project.getId(),
                    project.getName(),
                    projectMember.getProjectRole(),
                    project.getTopicState(),
                    memberCount,
                    project.getStartedAt(),
                    project.getDueAt()
            );
        });
    }

    @Transactional(readOnly = true)
    public ProjectDetailResponse getProjectDetail(Long userId, Long projectId) {
        validateUserExists(userId);
        Project project = getProject(projectId);

        validateProjectMember(projectId, userId);

        List<ProjectMember> projectMembers =
                projectMemberRepository.findAllWithUserByProjectId(projectId);

        ProjectMember ownerMember = projectMembers.stream()
                .filter(ProjectMember::isOwner)
                .findFirst()
                .orElseThrow(() -> new BusinessException(ErrorCode.PROJECT_MEMBER_NOT_FOUND));

        List<ProjectMemberResponse> members = projectMembers.stream()
                .map(pm -> {
                    User user = pm.getUser();
                    Long positionId = user.getPosition() != null ? user.getPosition().getId() : null;

                    return ProjectMemberResponse.of(
                            user.getId(),
                            user.getNickname(),
                            pm.getProjectRole(),
                            positionId
                    );
                })
                .toList();

        List<Long> domainIds = projectDomainRepository.findByProjectId(projectId).stream()
                .map(pd -> pd.getDomain().getId())
                .toList();

        return ProjectDetailResponse.of(
                project.getId(),
                project.getName(),
                project.getDescription(),
                project.getStartedAt(),
                project.getDueAt(),
                project.getInviteCode(),
                project.getTopicState(),
                ProjectOwnerResponse.of(
                        ownerMember.getUser().getId(),
                        ownerMember.getUser().getNickname()
                ),
                domainIds,
                projectMembers.size(),
                members
        );
    }

    private void validateUserExists(Long userId) {
        userRepository.findById(userId)
                .orElseThrow(() -> new BusinessException(ErrorCode.USER_NOT_FOUND));
    }

    private Project getProject(Long projectId) {
        return projectRepository.findById(projectId)
                .orElseThrow(() -> new BusinessException(ErrorCode.PROJECT_NOT_FOUND));
    }

    private void validateProjectMember(Long projectId, Long userId) {
        projectMemberRepository.findByProject_IdAndUser_Id(
                projectId,
                userId
        ).orElseThrow(() -> new BusinessException(ErrorCode.PROJECT_MEMBER_NOT_FOUND));
    }
}
