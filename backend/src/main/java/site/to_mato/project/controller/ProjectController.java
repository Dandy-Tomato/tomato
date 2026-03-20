package site.to_mato.project.controller;

import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import site.to_mato.common.response.ApiResponse;
import site.to_mato.project.dto.ProjectRequestDto;
import site.to_mato.project.dto.ProjectResponseDto;
import site.to_mato.project.service.ProjectService;

import java.util.List;

@RestController
@RequestMapping("/projects")
@RequiredArgsConstructor
public class ProjectController {

    private final ProjectService projectService;

    @PostMapping
    public ResponseEntity<ApiResponse<ProjectResponseDto.CreateData>> createProject(
            @Valid @RequestBody ProjectRequestDto.Create request
    ) {
        ProjectResponseDto.CreateData data = projectService.createProject(request);
        return ResponseEntity.status(HttpStatus.CREATED)
                .body(ApiResponse.ok(data));
    }

    @GetMapping("/me")
    public ResponseEntity<ApiResponse<List<ProjectResponseDto.MyProjectItem>>> getMyProjects() {
        List<ProjectResponseDto.MyProjectItem> data = projectService.getMyProjects();
        return ResponseEntity.ok(ApiResponse.ok(data));
    }

    @GetMapping("/{projectId}")
    public ResponseEntity<ApiResponse<ProjectResponseDto.DetailData>> getProjectDetail(
            @PathVariable Long projectId
    ) {
        ProjectResponseDto.DetailData data = projectService.getProjectDetail(projectId);
        return ResponseEntity.ok(ApiResponse.ok(data));
    }

    @PatchMapping("/{projectId}")
    public ResponseEntity<ApiResponse<ProjectResponseDto.UpdateData>> updateProject(
            @PathVariable Long projectId,
            @Valid @RequestBody ProjectRequestDto.Update request
    ) {
        ProjectResponseDto.UpdateData data = projectService.updateProject(projectId, request);
        return ResponseEntity.ok(ApiResponse.ok(data));
    }

    @DeleteMapping("/{projectId}")
    public ResponseEntity<ApiResponse<ProjectResponseDto.DeleteData>> deleteProject(
            @PathVariable Long projectId
    ) {
        ProjectResponseDto.DeleteData data = projectService.deleteProject(projectId);
        return ResponseEntity.ok(ApiResponse.ok(data));
    }

    @PatchMapping("/{projectId}/topic-confirmation")
    public ResponseEntity<ApiResponse<ProjectResponseDto.TopicConfirmationData>> confirmProjectTopic(
            @PathVariable Long projectId,
            @Valid @RequestBody ProjectRequestDto.ConfirmTopic request
    ) {
        ProjectResponseDto.TopicConfirmationData data = projectService.confirmProjectTopic(projectId, request);
        return ResponseEntity.ok(ApiResponse.ok(data));
    }

    @DeleteMapping("/{projectId}/topic-confirmation")
    public ResponseEntity<ApiResponse<ProjectResponseDto.TopicConfirmationData>> clearProjectTopic(
            @PathVariable Long projectId
    ) {
        ProjectResponseDto.TopicConfirmationData data = projectService.clearProjectTopic(projectId);
        return ResponseEntity.ok(ApiResponse.ok(data));
    }

    @GetMapping("/invite-codes/{inviteCode}")
    public ResponseEntity<ApiResponse<ProjectResponseDto.InviteLookupData>> lookupInviteCode(
            @PathVariable String inviteCode
    ) {
        ProjectResponseDto.InviteLookupData data = projectService.lookupInviteCode(inviteCode);
        return ResponseEntity.ok(ApiResponse.ok(data));
    }

    @PostMapping("/join")
    public ResponseEntity<ApiResponse<ProjectResponseDto.JoinData>> joinProject(
            @Valid @RequestBody ProjectRequestDto.Join request
    ) {
        ProjectResponseDto.JoinData data = projectService.joinProject(request);
        return ResponseEntity.status(HttpStatus.CREATED)
                .body(ApiResponse.ok(data));
    }

    @GetMapping("/{projectId}/members")
    public ResponseEntity<ApiResponse<List<ProjectResponseDto.ProjectMemberItem>>> getProjectMembers(
            @PathVariable Long projectId
    ) {
        List<ProjectResponseDto.ProjectMemberItem> data = projectService.getProjectMembers(projectId);
        return ResponseEntity.ok(ApiResponse.ok(data));
    }

    @DeleteMapping("/{projectId}/members/me")
    public ResponseEntity<ApiResponse<ProjectResponseDto.LeaveData>> leaveProject(
            @PathVariable Long projectId
    ) {
        ProjectResponseDto.LeaveData data = projectService.leaveProject(projectId);
        return ResponseEntity.ok(ApiResponse.ok(data));
    }

    @PatchMapping("/{projectId}/owner")
    public ResponseEntity<ApiResponse<ProjectResponseDto.TransferOwnerData>> transferOwner(
            @PathVariable Long projectId,
            @Valid @RequestBody ProjectRequestDto.TransferOwner request
    ) {
        ProjectResponseDto.TransferOwnerData data = projectService.transferOwner(projectId, request);
        return ResponseEntity.ok(ApiResponse.ok(data));
    }

    @GetMapping("/{projectId}/domains")
    public ResponseEntity<ApiResponse<List<ProjectResponseDto.ProjectDomainItem>>> getProjectDomains(
            @PathVariable Long projectId
    ) {
        List<ProjectResponseDto.ProjectDomainItem> data = projectService.getProjectDomains(projectId);
        return ResponseEntity.ok(ApiResponse.ok(data));
    }

    @GetMapping("/{projectId}/skills")
    public ResponseEntity<ApiResponse<List<ProjectResponseDto.ProjectSkillItem>>> getProjectSkills(
            @PathVariable Long projectId
    ) {
        List<ProjectResponseDto.ProjectSkillItem> data = projectService.getProjectSkills(projectId);
        return ResponseEntity.ok(ApiResponse.ok(data));
    }
}