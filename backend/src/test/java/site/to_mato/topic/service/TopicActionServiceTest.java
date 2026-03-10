package site.to_mato.topic.service;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.mockito.*;
import org.springframework.dao.DataIntegrityViolationException;
import org.springframework.orm.ObjectOptimisticLockingFailureException;
import site.to_mato.common.exception.BusinessException;
import site.to_mato.common.exception.ErrorCode;
import site.to_mato.project.entity.Project;
import site.to_mato.project.repository.ProjectRepository;
import site.to_mato.topic.entity.ProjectTopicReaction;
import site.to_mato.topic.entity.Topic;
import site.to_mato.topic.entity.enums.Reaction;
import site.to_mato.topic.repository.ProjectTopicReactionRepository;
import site.to_mato.topic.repository.TopicRepository;

import java.util.Optional;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;

class TopicActionServiceTest {

    @InjectMocks
    private TopicActionService topicActionService;

    @Mock
    private ProjectTopicReactionRepository reactionRepository;

    @Mock
    private ProjectRepository projectRepository;

    @Mock
    private TopicRepository topicRepository;

    @BeforeEach
    void setUp() {
        MockitoAnnotations.openMocks(this);
    }

    @DisplayName("reaction 없으면 생성")
    @Test
    void react_shouldCreateReaction_whenReactionNotExists() {
        Long projectId = 1L;
        Long topicId = 1L;

        when(reactionRepository.findByProjectIdAndTopicId(projectId, topicId))
                .thenReturn(Optional.empty());
        when(projectRepository.getReferenceById(projectId)).thenReturn(new Project());
        when(topicRepository.getReferenceById(topicId)).thenReturn(new Topic());

        topicActionService.react(projectId, topicId, Reaction.LIKE);

        verify(reactionRepository).save(any(ProjectTopicReaction.class));
        verify(reactionRepository).flush();
    }

    @DisplayName("기존 reaction과 같으면 삭제")
    @Test
    void react_shouldDeleteReaction_whenReactionSameAsExisting() {
        ProjectTopicReaction existing = ProjectTopicReaction.of(new Project(), new Topic(), Reaction.LIKE);

        when(reactionRepository.findByProjectIdAndTopicId(1L, 1L))
                .thenReturn(Optional.of(existing));

        topicActionService.react(1L, 1L, Reaction.LIKE);

        verify(reactionRepository).delete(existing);
        verify(reactionRepository).flush();
    }

    @DisplayName("기존 reaction과 다르면 수정")
    @Test
    void react_shouldUpdateReaction_whenReactionDifferent() {
        ProjectTopicReaction existing = ProjectTopicReaction.of(new Project(), new Topic(), Reaction.LIKE);

        when(reactionRepository.findByProjectIdAndTopicId(1L, 1L))
                .thenReturn(Optional.of(existing));

        topicActionService.react(1L, 1L, Reaction.DISLIKE);

        assertEquals(Reaction.DISLIKE, existing.getReaction());
        verify(reactionRepository).flush();
    }

    @DisplayName("낙관적 락 예외 발생 시 BusinessException 변환")
    @Test
    void react_shouldThrowBusinessException_whenOptimisticLockExceptionOccurs() {
        ProjectTopicReaction existing = ProjectTopicReaction.of(new Project(), new Topic(), Reaction.LIKE);

        when(reactionRepository.findByProjectIdAndTopicId(1L, 1L))
                .thenReturn(Optional.of(existing));
        doThrow(ObjectOptimisticLockingFailureException.class)
                .when(reactionRepository).flush();

        BusinessException exception = assertThrows(BusinessException.class,
                () -> topicActionService.react(1L, 1L, Reaction.DISLIKE));

        assertEquals(ErrorCode.REACTION_CONFLICT, exception.getErrorCode());
    }

    @DisplayName("데이터 무결성 예외 발생 시 BusinessException 변환")
    @Test
    void react_shouldThrowBusinessException_whenDataIntegrityViolationOccurs() {
        when(reactionRepository.findByProjectIdAndTopicId(1L, 1L))
                .thenReturn(Optional.empty());
        when(projectRepository.getReferenceById(1L)).thenReturn(new Project());
        when(topicRepository.getReferenceById(1L)).thenReturn(new Topic());
        doThrow(DataIntegrityViolationException.class)
                .when(reactionRepository).save(any(ProjectTopicReaction.class));

        BusinessException exception = assertThrows(BusinessException.class,
                () -> topicActionService.react(1L, 1L, Reaction.LIKE));

        assertEquals(ErrorCode.REACTION_CONFLICT, exception.getErrorCode());
    }
}
