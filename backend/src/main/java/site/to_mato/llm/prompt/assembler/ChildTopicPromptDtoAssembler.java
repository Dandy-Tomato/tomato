package site.to_mato.llm.prompt.assembler;

import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Component;
import site.to_mato.project.entity.Project;
import site.to_mato.project.repository.ProjectDomainRepository;
import site.to_mato.project.repository.ProjectMemberRepository;
import site.to_mato.project.repository.ProjectSkillRepository;
import site.to_mato.llm.prompt.model.ChildTopicPromptDto;
import site.to_mato.topic.entity.Topic;

import java.util.List;

@Component
@RequiredArgsConstructor
public class ChildTopicPromptDtoAssembler {

    private final ProjectMemberRepository memberRepository;
    private final ProjectSkillRepository skillRepository;
    private final ProjectDomainRepository domainRepository;

    public ChildTopicPromptDto assemble(Project project, Topic topic) {
        int memberCount = resolveMemberCount(project);
        List<String> skills = resolveSkills(project);
        List<String> domains = resolveDomains(project);

        return ChildTopicPromptDto.of(
                project,
                topic,
                memberCount,
                skills,
                domains
        );
    }

    private int resolveMemberCount(Project project) {
        long count = memberRepository.countMembersByProjectIds(List.of(project.getId()))
                .stream()
                .mapToLong(row -> (Long) row[1])
                .sum();

        return count == 0 ? 1 : (int) count;
    }

    private List<String> resolveSkills(Project project) {
        return skillRepository.findAllByProject_Id(project.getId())
                .stream()
                .map(ps -> ps.getSkill().getName())
                .toList();
    }

    private List<String> resolveDomains(Project project) {
        return domainRepository.findByProjectId(project.getId())
                .stream()
                .map(pd -> pd.getDomain().getName())
                .toList();
    }
}
