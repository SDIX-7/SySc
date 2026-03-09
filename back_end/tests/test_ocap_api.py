import pytest
from datetime import datetime


class TestOCAPMainAPI:
    
    def test_create_ocap_success(self, client, sample_ocap):
        response = client.post("/api/ocaps", json=sample_ocap)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == sample_ocap["name"]
        assert data["description"] == sample_ocap["description"]
        assert data["priority"] == sample_ocap["priority"]
        assert data["status"] == sample_ocap["status"]
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data

    def test_create_ocap_with_nested_data(self, client, sample_ocap_with_nested):
        response = client.post("/api/ocaps", json=sample_ocap_with_nested)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == sample_ocap_with_nested["name"]
        assert len(data["signals"]) == 1
        assert len(data["steps"]) == 2
        assert data["signals"][0]["signal_type"] == "run_9"
        assert data["steps"][0]["phase"] == "containment"

    def test_create_ocap_missing_required_field(self, client):
        invalid_ocap = {
            "description": "缺少name字段"
        }
        response = client.post("/api/ocaps", json=invalid_ocap)
        assert response.status_code == 422

    def test_get_ocaps_list(self, client, sample_ocap):
        client.post("/api/ocaps", json=sample_ocap)
        response = client.get("/api/ocaps")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    def test_get_ocaps_filter_by_status(self, client, sample_ocap):
        client.post("/api/ocaps", json=sample_ocap)
        response = client.get("/api/ocaps?status=draft")
        assert response.status_code == 200
        data = response.json()
        assert all(ocap["status"] == "draft" for ocap in data)

    def test_get_ocaps_filter_by_priority(self, client, sample_ocap):
        client.post("/api/ocaps", json=sample_ocap)
        response = client.get("/api/ocaps?priority=high")
        assert response.status_code == 200
        data = response.json()
        assert all(ocap["priority"] == "high" for ocap in data)

    def test_get_ocap_by_id(self, client, sample_ocap):
        create_response = client.post("/api/ocaps", json=sample_ocap)
        ocap_id = create_response.json()["id"]
        
        response = client.get(f"/api/ocaps/{ocap_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == ocap_id
        assert data["name"] == sample_ocap["name"]

    def test_get_ocap_not_found(self, client):
        response = client.get("/api/ocaps/99999")
        assert response.status_code == 404
        assert "OCAP不存在" in response.json()["detail"]

    def test_update_ocap(self, client, sample_ocap):
        create_response = client.post("/api/ocaps", json=sample_ocap)
        ocap_id = create_response.json()["id"]
        
        update_data = {
            "name": "更新后的OCAP名称",
            "status": "active",
            "priority": "critical"
        }
        response = client.put(f"/api/ocaps/{ocap_id}", json=update_data)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "更新后的OCAP名称"
        assert data["status"] == "active"
        assert data["priority"] == "critical"

    def test_update_ocap_not_found(self, client):
        update_data = {"name": "不存在的OCAP"}
        response = client.put("/api/ocaps/99999", json=update_data)
        assert response.status_code == 404

    def test_delete_ocap(self, client, sample_ocap):
        create_response = client.post("/api/ocaps", json=sample_ocap)
        ocap_id = create_response.json()["id"]
        
        response = client.delete(f"/api/ocaps/{ocap_id}")
        assert response.status_code == 200
        assert "OCAP删除成功" in response.json()["message"]
        
        get_response = client.get(f"/api/ocaps/{ocap_id}")
        assert get_response.status_code == 404

    def test_delete_ocap_not_found(self, client):
        response = client.delete("/api/ocaps/99999")
        assert response.status_code == 404

    def test_delete_ocap_cascades(self, client, sample_ocap_with_nested):
        create_response = client.post("/api/ocaps", json=sample_ocap_with_nested)
        ocap_id = create_response.json()["id"]
        
        client.delete(f"/api/ocaps/{ocap_id}")
        
        signals_response = client.get(f"/api/ocaps/{ocap_id}/signals")
        steps_response = client.get(f"/api/ocaps/{ocap_id}/steps")
        assert signals_response.status_code == 404
        assert steps_response.status_code == 404


class TestOCAPSignalAPI:
    
    def test_create_ocap_signal(self, client, sample_ocap, sample_ocap_signal):
        create_response = client.post("/api/ocaps", json=sample_ocap)
        ocap_id = create_response.json()["id"]
        
        response = client.post(f"/api/ocaps/{ocap_id}/signals", json=sample_ocap_signal)
        assert response.status_code == 200
        data = response.json()
        assert data["signal_type"] == sample_ocap_signal["signal_type"]
        assert data["signal_value"] == sample_ocap_signal["signal_value"]
        assert data["ocap_id"] == ocap_id

    def test_get_ocap_signals(self, client, sample_ocap, sample_ocap_signal):
        create_response = client.post("/api/ocaps", json=sample_ocap)
        ocap_id = create_response.json()["id"]
        client.post(f"/api/ocaps/{ocap_id}/signals", json=sample_ocap_signal)
        
        response = client.get(f"/api/ocaps/{ocap_id}/signals")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    def test_delete_ocap_signal(self, client, sample_ocap, sample_ocap_signal):
        create_response = client.post("/api/ocaps", json=sample_ocap)
        ocap_id = create_response.json()["id"]
        signal_response = client.post(f"/api/ocaps/{ocap_id}/signals", json=sample_ocap_signal)
        signal_id = signal_response.json()["id"]
        
        response = client.delete(f"/api/ocaps/{ocap_id}/signals/{signal_id}")
        assert response.status_code == 200
        assert "OCAP信号删除成功" in response.json()["message"]

    def test_signal_invalid_ocap_id(self, client, sample_ocap_signal):
        response = client.post("/api/ocaps/99999/signals", json=sample_ocap_signal)
        assert response.status_code == 404


class TestOCAPStepAPI:
    
    def test_create_ocap_step(self, client, sample_ocap, sample_ocap_step):
        create_response = client.post("/api/ocaps", json=sample_ocap)
        ocap_id = create_response.json()["id"]
        
        response = client.post(f"/api/ocaps/{ocap_id}/steps", json=sample_ocap_step)
        assert response.status_code == 200
        data = response.json()
        assert data["action_description"] == sample_ocap_step["action_description"]
        assert data["phase"] == sample_ocap_step["phase"]

    def test_get_ocap_steps_ordered(self, client, sample_ocap):
        create_response = client.post("/api/ocaps", json=sample_ocap)
        ocap_id = create_response.json()["id"]
        
        step1 = {"phase": "containment", "step_number": 1, "sort_order": 2}
        step2 = {"phase": "investigation", "step_number": 2, "sort_order": 1}
        client.post(f"/api/ocaps/{ocap_id}/steps", json=step1)
        client.post(f"/api/ocaps/{ocap_id}/steps", json=step2)
        
        response = client.get(f"/api/ocaps/{ocap_id}/steps")
        assert response.status_code == 200
        data = response.json()
        assert data[0]["sort_order"] == 1
        assert data[1]["sort_order"] == 2

    def test_update_ocap_step(self, client, sample_ocap, sample_ocap_step):
        create_response = client.post("/api/ocaps", json=sample_ocap)
        ocap_id = create_response.json()["id"]
        step_response = client.post(f"/api/ocaps/{ocap_id}/steps", json=sample_ocap_step)
        step_id = step_response.json()["id"]
        
        update_data = {
            "action_description": "更新后的步骤描述",
            "status": "completed"
        }
        response = client.put(f"/api/ocaps/{ocap_id}/steps/{step_id}", json=update_data)
        assert response.status_code == 200
        data = response.json()
        assert data["action_description"] == "更新后的步骤描述"

    def test_delete_ocap_step(self, client, sample_ocap, sample_ocap_step):
        create_response = client.post("/api/ocaps", json=sample_ocap)
        ocap_id = create_response.json()["id"]
        step_response = client.post(f"/api/ocaps/{ocap_id}/steps", json=sample_ocap_step)
        step_id = step_response.json()["id"]
        
        response = client.delete(f"/api/ocaps/{ocap_id}/steps/{step_id}")
        assert response.status_code == 200
        assert "OCAP步骤删除成功" in response.json()["message"]


class TestOCAPExecutionAPI:
    
    def test_create_ocap_execution(self, client, sample_ocap, sample_ocap_execution):
        create_response = client.post("/api/ocaps", json=sample_ocap)
        ocap_id = create_response.json()["id"]
        
        response = client.post(f"/api/ocaps/{ocap_id}/executions", json=sample_ocap_execution)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == sample_ocap_execution["status"]
        assert data["executed_by"] == sample_ocap_execution["executed_by"]

    def test_get_ocap_executions(self, client, sample_ocap, sample_ocap_execution):
        create_response = client.post("/api/ocaps", json=sample_ocap)
        ocap_id = create_response.json()["id"]
        client.post(f"/api/ocaps/{ocap_id}/executions", json=sample_ocap_execution)
        
        response = client.get(f"/api/ocaps/{ocap_id}/executions")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    def test_update_ocap_execution(self, client, sample_ocap, sample_ocap_execution):
        create_response = client.post("/api/ocaps", json=sample_ocap)
        ocap_id = create_response.json()["id"]
        exec_response = client.post(f"/api/ocaps/{ocap_id}/executions", json=sample_ocap_execution)
        exec_id = exec_response.json()["id"]
        
        update_data = {
            "status": "completed",
            "completed_at": "2026-03-07T12:00:00",
            "notes": "执行完成"
        }
        response = client.put(f"/api/ocaps/{ocap_id}/executions/{exec_id}", json=update_data)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "completed"

    def test_delete_ocap_execution(self, client, sample_ocap, sample_ocap_execution):
        create_response = client.post("/api/ocaps", json=sample_ocap)
        ocap_id = create_response.json()["id"]
        exec_response = client.post(f"/api/ocaps/{ocap_id}/executions", json=sample_ocap_execution)
        exec_id = exec_response.json()["id"]
        
        response = client.delete(f"/api/ocaps/{ocap_id}/executions/{exec_id}")
        assert response.status_code == 200


class TestOCAPRootCauseAPI:
    
    def test_create_ocap_root_cause(self, client, sample_ocap, sample_ocap_root_cause):
        create_response = client.post("/api/ocaps", json=sample_ocap)
        ocap_id = create_response.json()["id"]
        
        response = client.post(f"/api/ocaps/{ocap_id}/root-causes", json=sample_ocap_root_cause)
        assert response.status_code == 200
        data = response.json()
        assert data["analysis_method"] == "5whys"
        assert data["why_1"] == sample_ocap_root_cause["why_1"]
        assert len(data["contributing_factors"]) == 2

    def test_get_ocap_root_causes(self, client, sample_ocap, sample_ocap_root_cause):
        create_response = client.post("/api/ocaps", json=sample_ocap)
        ocap_id = create_response.json()["id"]
        client.post(f"/api/ocaps/{ocap_id}/root-causes", json=sample_ocap_root_cause)
        
        response = client.get(f"/api/ocaps/{ocap_id}/root-causes")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    def test_update_ocap_root_cause(self, client, sample_ocap, sample_ocap_root_cause):
        create_response = client.post("/api/ocaps", json=sample_ocap)
        ocap_id = create_response.json()["id"]
        rc_response = client.post(f"/api/ocaps/{ocap_id}/root-causes", json=sample_ocap_root_cause)
        rc_id = rc_response.json()["id"]
        
        update_data = {
            "verified": True,
            "verified_by": "验证人",
            "root_cause_description": "更新后的根本原因描述"
        }
        response = client.put(f"/api/ocaps/{ocap_id}/root-causes/{rc_id}", json=update_data)
        assert response.status_code == 200
        data = response.json()
        assert data["verified"] == True

    def test_delete_ocap_root_cause(self, client, sample_ocap, sample_ocap_root_cause):
        create_response = client.post("/api/ocaps", json=sample_ocap)
        ocap_id = create_response.json()["id"]
        rc_response = client.post(f"/api/ocaps/{ocap_id}/root-causes", json=sample_ocap_root_cause)
        rc_id = rc_response.json()["id"]
        
        response = client.delete(f"/api/ocaps/{ocap_id}/root-causes/{rc_id}")
        assert response.status_code == 200


class TestOCAPCorrectiveActionAPI:
    
    def test_create_ocap_corrective_action(self, client, sample_ocap, sample_ocap_corrective_action):
        create_response = client.post("/api/ocaps", json=sample_ocap)
        ocap_id = create_response.json()["id"]
        
        response = client.post(f"/api/ocaps/{ocap_id}/corrective-actions", json=sample_ocap_corrective_action)
        assert response.status_code == 200
        data = response.json()
        assert data["action_description"] == sample_ocap_corrective_action["action_description"]
        assert data["action_type"] == "permanent"

    def test_create_corrective_action_with_root_cause(self, client, sample_ocap, sample_ocap_root_cause, sample_ocap_corrective_action):
        create_response = client.post("/api/ocaps", json=sample_ocap)
        ocap_id = create_response.json()["id"]
        rc_response = client.post(f"/api/ocaps/{ocap_id}/root-causes", json=sample_ocap_root_cause)
        rc_id = rc_response.json()["id"]
        
        ca_with_rc = {**sample_ocap_corrective_action, "root_cause_id": rc_id}
        response = client.post(f"/api/ocaps/{ocap_id}/corrective-actions", json=ca_with_rc)
        assert response.status_code == 200
        data = response.json()
        assert data["root_cause_id"] == rc_id

    def test_get_ocap_corrective_actions(self, client, sample_ocap, sample_ocap_corrective_action):
        create_response = client.post("/api/ocaps", json=sample_ocap)
        ocap_id = create_response.json()["id"]
        client.post(f"/api/ocaps/{ocap_id}/corrective-actions", json=sample_ocap_corrective_action)
        
        response = client.get(f"/api/ocaps/{ocap_id}/corrective-actions")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    def test_update_ocap_corrective_action(self, client, sample_ocap, sample_ocap_corrective_action):
        create_response = client.post("/api/ocaps", json=sample_ocap)
        ocap_id = create_response.json()["id"]
        ca_response = client.post(f"/api/ocaps/{ocap_id}/corrective-actions", json=sample_ocap_corrective_action)
        ca_id = ca_response.json()["id"]
        
        update_data = {
            "status": "completed",
            "effectiveness_verified": True,
            "verification_result": "措施有效，问题已解决"
        }
        response = client.put(f"/api/ocaps/{ocap_id}/corrective-actions/{ca_id}", json=update_data)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "completed"
        assert data["effectiveness_verified"] == True

    def test_delete_ocap_corrective_action(self, client, sample_ocap, sample_ocap_corrective_action):
        create_response = client.post("/api/ocaps", json=sample_ocap)
        ocap_id = create_response.json()["id"]
        ca_response = client.post(f"/api/ocaps/{ocap_id}/corrective-actions", json=sample_ocap_corrective_action)
        ca_id = ca_response.json()["id"]
        
        response = client.delete(f"/api/ocaps/{ocap_id}/corrective-actions/{ca_id}")
        assert response.status_code == 200

    def test_corrective_action_invalid_root_cause(self, client, sample_ocap, sample_ocap_corrective_action):
        create_response = client.post("/api/ocaps", json=sample_ocap)
        ocap_id = create_response.json()["id"]
        
        ca_invalid = {**sample_ocap_corrective_action, "root_cause_id": 99999}
        response = client.post(f"/api/ocaps/{ocap_id}/corrective-actions", json=ca_invalid)
        assert response.status_code == 404
