package site.to_mato.project.service;

import site.to_mato.project.dto.ProjectRequestDto;
import site.to_mato.project.dto.ProjectResponseDto;

import java.util.List;

public interface ProjectService {

    ProjectResponseDto.CreateData createProject(ProjectRequestDto.Create request);

    List<ProjectResponseDto.MyProjectItem> getMyProjects();

    ProjectResponseDto.DetailData getProjectDetail(Long projectId);

    ProjectResponseDto.UpdateData updateProject(Long projectId, ProjectRequestDto.Update request);

    ProjectResponseDto.DeleteData deleteProject(Long projectId);

    ProjectResponseDto.TopicConfirmationData confirmProjectTopic(Long projectId, ProjectRequestDto.ConfirmTopic request);

    ProjectResponseDto.TopicConfirmationData clearProjectTopic(Long projectId);

    ProjectResponseDto.InviteLookupData lookupInviteCode(String inviteCode);

    ProjectResponseDto.JoinData joinProject(ProjectRequestDto.Join request);

    List<ProjectResponseDto.ProjectMemberItem> getProjectMembers(Long projectId);

    ProjectResponseDto.LeaveData leaveProject(Long projectId);

    ProjectResponseDto.TransferOwnerData transferOwner(Long projectId, ProjectRequestDto.TransferOwner request);

    List<ProjectResponseDto.ProjectDomainItem> getProjectDomains(Long projectId);

    List<ProjectResponseDto.ProjectSkillItem> getProjectSkills(Long projectId);

    void refreshProjectSkillsForUser(Long userId);
}