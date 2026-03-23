package site.to_mato.project.service;

import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import site.to_mato.common.exception.BusinessException;
import site.to_mato.common.exception.ErrorCode;
import site.to_mato.project.dto.request.ConfirmProjectTopicRequest;
import site.to_mato.project.dto.response.ConfirmedProjectTopicResponse;
import site.to_mato.project.entity.Project;
import site.to_mato.project.entity.ProjectMember;
import site.to_mato.project.repository.ProjectMemberRepository;
import site.to_mato.project.repository.ProjectRepository;
import site.to_mato.topic.entity.ChildTopic;
import site.to_mato.topic.repository.ChildTopicRepository;
import site.to_mato.user.repository.UserRepository;

@Service
@RequiredArgsConstructor
public class ProjectTopicService {

    private final ProjectRepository projectRepository;
    private final ProjectMemberRepository projectMemberRepository;

    private final UserRepository userRepository;
    private final ChildTopicRepository childTopicRepository;

    @Transactional
    public ConfirmedProjectTopicResponse confirmProjectTopic(Long userId, Long projectId, ConfirmProjectTopicRequest request) {
        getUser(userId);
        Project project = getProject(projectId);
        ProjectMember projectMember = getProjectMember(projectId, userId);

        validateProjectOwner(projectMember);

        ChildTopic childTopic = getChildTopic(request.childTopicId());

        if (!childTopic.getProject().getId().equals(projectId)) {
            throw new BusinessException(ErrorCode.PROJECT_FORBIDDEN);
        }

        project.confirmTopic(childTopic);

        return ConfirmedProjectTopicResponse.of(project.getId(), true, childTopic.getId());
    }

    @Transactional
    public ConfirmedProjectTopicResponse clearConfirmedProjectTopic(Long userId, Long projectId) {
        getUser(userId);
        Project project = getProject(projectId);
        ProjectMember projectMember = getProjectMember(projectId, userId);

        validateProjectOwner(projectMember);

        project.clearConfirmedTopic();

        return ConfirmedProjectTopicResponse.of(project.getId(), false, null);
    }

    private void getUser(Long userId) {
        userRepository.findByIdAndDeletedAtIsNull(userId)
                .orElseThrow(() -> new BusinessException(ErrorCode.USER_NOT_FOUND));
    }

    private Project getProject(Long projectId) {
        return projectRepository.findByIdAndDeletedAtIsNull(projectId)
                .orElseThrow(() -> new BusinessException(ErrorCode.PROJECT_NOT_FOUND));
    }

    private ProjectMember getProjectMember(Long projectId, Long userId) {
        return projectMemberRepository.findByProjectIdAndUserIdAndProjectDeletedAtIsNullAndUserDeletedAtIsNull(
                projectId,
                userId
        ).orElseThrow(() -> new BusinessException(ErrorCode.PROJECT_MEMBER_NOT_FOUND));
    }

    private void validateProjectOwner(ProjectMember projectMember) {
        if (!projectMember.isOwner()) {
            throw new BusinessException(ErrorCode.PROJECT_FORBIDDEN);
        }
    }

    private ChildTopic getChildTopic(Long childTopicId) {
        return childTopicRepository.findById(childTopicId)
                .orElseThrow(() -> new BusinessException(ErrorCode.CHILD_TOPIC_NOT_FOUND));
    }
}
