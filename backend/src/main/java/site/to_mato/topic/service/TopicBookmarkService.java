package site.to_mato.topic.service;

import jakarta.transaction.Transactional;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import site.to_mato.project.entity.Project;
import site.to_mato.project.repository.ProjectRepository;
import site.to_mato.topic.entity.ProjectTopicBookmark;
import site.to_mato.topic.entity.Topic;
import site.to_mato.topic.repository.ProjectTopicBookmarkRepository;
import site.to_mato.topic.repository.TopicRepository;

@Service
@RequiredArgsConstructor
public class TopicBookmarkService {

    private final TopicRepository topicRepository;
    private final ProjectRepository projectRepository;
    private final ProjectTopicBookmarkRepository bookmarkRepository;

    @Transactional
    public boolean toggleBookmark(Long projectId, Long topicId) {

        boolean isBookmarked = bookmarkRepository.existsByProjectIdAndTopicId(projectId, topicId);
        if (isBookmarked) {
            bookmarkRepository.deleteByProjectIdAndTopicId(projectId, topicId);
            return false;
        }

        Project project = projectRepository.getReferenceById(projectId);
        Topic topic = topicRepository.getReferenceById(topicId);

        bookmarkRepository.save(ProjectTopicBookmark.of(project, topic));

        return true;
    }

}
