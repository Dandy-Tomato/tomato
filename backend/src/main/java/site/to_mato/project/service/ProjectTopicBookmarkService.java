package site.to_mato.project.service;

import jakarta.transaction.Transactional;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import site.to_mato.project.entity.Project;
import site.to_mato.project.entity.ProjectTopicBookmark;
import site.to_mato.project.repository.ProjectRepository;
import site.to_mato.project.repository.ProjectTopicBookmarkRepository;
import site.to_mato.recommendation.entity.enums.ActionType;
import site.to_mato.recommendation.service.ActionLogService;
import site.to_mato.topic.entity.Topic;
import site.to_mato.topic.repository.TopicRepository;

@Service
@RequiredArgsConstructor
public class ProjectTopicBookmarkService {

    private final TopicRepository topicRepository;
    private final ActionLogService actionLogService;
    private final ProjectRepository projectRepository;
    private final ProjectTopicBookmarkRepository bookmarkRepository;

    @Transactional
    public boolean toggleBookmark(Long actorUserId, Long projectId, Long topicId) {

        ProjectTopicBookmark bookmark = bookmarkRepository
                .findByProject_IdAndTopic_Id(projectId, topicId)
                .orElse(null);

        if (bookmark != null) {
            bookmarkRepository.delete(bookmark);
            return false;
        }

        Project project = projectRepository.getReferenceById(projectId);
        Topic topic = topicRepository.getReferenceById(topicId);

        bookmarkRepository.save(ProjectTopicBookmark.of(project, topic));
        actionLogService.createActionLog(actorUserId, projectId, topicId, ActionType.BOOKMARK);

        return true;
    }
}
