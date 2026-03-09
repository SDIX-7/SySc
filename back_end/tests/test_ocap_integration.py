import pytest
from datetime import datetime


class TestOCAPIntegration:
    
    def test_complete_ocap_workflow(self, client):
        ocap_data = {
            "name": "完整工作流测试OCAP",
            "description": "测试OCAP完整生命周期",
            "signal_type": "point_beyond_3sigma",
            "priority": "critical",
            "severity_score": 9,
            "scope_score": 8,
            "trend_score": 7,
            "overall_priority_score": 8,
            "status": "draft",
            "is_active": True,
            "created_by": "集成测试"
        }
        
        create_response = client.post("/api/ocaps", json=ocap_data)
        assert create_response.status_code == 200
        ocap_id = create_response.json()["id"]
        
        signal_data = {
            "signal_time": "2026-03-07T10:00:00",
            "signal_type": "point_beyond_3sigma",
            "signal_value": "0.95",
            "control_limit_value": "0.50",
            "subgroup_index": 10,
            "raw_data_snapshot": {"values": [0.1, 0.2, 0.3]},
            "detected_by": "auto"
        }
        signal_response = client.post(f"/api/ocaps/{ocap_id}/signals", json=signal_data)
        assert signal_response.status_code == 200
        
        steps_data = [
            {
                "phase": "containment",
                "step_number": 1,
                "action_type": "immediate",
                "action_description": "停止生产",
                "responsible_role": "操作员",
                "sort_order": 1
            },
            {
                "phase": "investigation",
                "step_number": 2,
                "action_type": "short_term",
                "action_description": "根本原因分析",
                "responsible_role": "质量工程师",
                "sort_order": 2
            }
        ]
        for step in steps_data:
            step_response = client.post(f"/api/ocaps/{ocap_id}/steps", json=step)
            assert step_response.status_code == 200
        
        update_response = client.put(f"/api/ocaps/{ocap_id}", json={"status": "active"})
        assert update_response.status_code == 200
        assert update_response.json()["status"] == "active"
        
        steps = client.get(f"/api/ocaps/{ocap_id}/steps").json()
        first_step_id = steps[0]["id"]
        
        execution_data = {
            "step_id": first_step_id,
            "status": "in_progress",
            "started_at": "2026-03-07T10:30:00",
            "executed_by": "张三"
        }
        exec_response = client.post(f"/api/ocaps/{ocap_id}/executions", json=execution_data)
        assert exec_response.status_code == 200
        exec_id = exec_response.json()["id"]
        
        exec_update = {
            "status": "completed",
            "completed_at": "2026-03-07T11:00:00",
            "notes": "遏制措施已完成"
        }
        exec_update_response = client.put(f"/api/ocaps/{ocap_id}/executions/{exec_id}", json=exec_update)
        assert exec_update_response.status_code == 200
        
        root_cause_data = {
            "analysis_method": "5whys",
            "why_1": "为什么出现缺陷？设备参数偏移",
            "why_2": "为什么设备参数偏移？维护不及时",
            "why_3": "为什么维护不及时？人员不足",
            "why_4": "为什么人员不足？预算削减",
            "why_5": "为什么预算削减？管理层决策",
            "root_cause_description": "根本原因：管理层预算决策导致维护人员不足"
        }
        rc_response = client.post(f"/api/ocaps/{ocap_id}/root-causes", json=root_cause_data)
        assert rc_response.status_code == 200
        rc_id = rc_response.json()["id"]
        
        rc_update = {
            "verified": True,
            "verified_by": "质量经理"
        }
        rc_update_response = client.put(f"/api/ocaps/{ocap_id}/root-causes/{rc_id}", json=rc_update)
        assert rc_update_response.status_code == 200
        
        corrective_action_data = {
            "root_cause_id": rc_id,
            "action_description": "增加维护人员编制",
            "action_type": "permanent",
            "responsible_person": "生产经理",
            "target_date": "2026-04-01",
            "status": "planned"
        }
        ca_response = client.post(f"/api/ocaps/{ocap_id}/corrective-actions", json=corrective_action_data)
        assert ca_response.status_code == 200
        ca_id = ca_response.json()["id"]
        
        ca_update = {
            "status": "completed",
            "actual_date": "2026-03-25",
            "effectiveness_verified": True,
            "verification_result": "措施有效，问题已解决"
        }
        ca_update_response = client.put(f"/api/ocaps/{ocap_id}/corrective-actions/{ca_id}", json=ca_update)
        assert ca_update_response.status_code == 200
        
        final_update = {"status": "completed"}
        final_response = client.put(f"/api/ocaps/{ocap_id}", json=final_update)
        assert final_response.status_code == 200
        assert final_response.json()["status"] == "completed"
        
        get_response = client.get(f"/api/ocaps/{ocap_id}")
        assert get_response.status_code == 200
        final_data = get_response.json()
        assert len(final_data["signals"]) == 1
        assert len(final_data["steps"]) == 2
        assert len(final_data["executions"]) == 1
        assert len(final_data["root_causes"]) == 1
        assert len(final_data["corrective_actions"]) == 1

    def test_ocap_with_control_chart_config(self, client, sample_production_line, sample_control_chart_config):
        line_response = client.post("/api/production-lines", json=sample_production_line)
        assert line_response.status_code == 200
        line_id = line_response.json()["id"]
        
        config_data = {**sample_control_chart_config, "line_id": line_id}
        config_response = client.post("/api/control-chart-config", json=config_data)
        assert config_response.status_code == 200
        config_id = config_response.json()["id"]
        
        ocap_data = {
            "control_chart_config_id": config_id,
            "line_id": line_id,
            "name": "关联控制图配置的OCAP",
            "description": "测试OCAP与控制图配置的关联",
            "signal_type": "run_9",
            "priority": "high",
            "status": "active"
        }
        ocap_response = client.post("/api/ocaps", json=ocap_data)
        assert ocap_response.status_code == 200
        
        ocaps_response = client.get(f"/api/control-chart-configs/{config_id}/ocaps")
        assert ocaps_response.status_code == 200
        ocaps = ocaps_response.json()
        assert len(ocaps) == 1
        assert ocaps[0]["control_chart_config_id"] == config_id

    def test_ocap_filtering_integration(self, client):
        ocap_data_list = [
            {"name": "OCAP-高优先级-草稿", "priority": "high", "status": "draft"},
            {"name": "OCAP-高优先级-激活", "priority": "high", "status": "active"},
            {"name": "OCAP-低优先级-草稿", "priority": "low", "status": "draft"},
            {"name": "OCAP-关键-执行中", "priority": "critical", "status": "executing"},
        ]
        
        for ocap_data in ocap_data_list:
            client.post("/api/ocaps", json=ocap_data)
        
        high_priority = client.get("/api/ocaps?priority=high").json()
        assert all(o["priority"] == "high" for o in high_priority)
        assert len(high_priority) == 2
        
        draft_status = client.get("/api/ocaps?status=draft").json()
        assert all(o["status"] == "draft" for o in draft_status)
        assert len(draft_status) == 2
        
        high_and_draft = client.get("/api/ocaps?priority=high&status=draft").json()
        assert len(high_and_draft) == 1
        assert high_and_draft[0]["name"] == "OCAP-高优先级-草稿"

    def test_ocap_deletion_cascades_all(self, client):
        ocap_data = {
            "name": "级联删除测试OCAP",
            "signals": [{"signal_type": "point_beyond_3sigma"}],
            "steps": [{"phase": "containment", "step_number": 1}]
        }
        create_response = client.post("/api/ocaps", json=ocap_data)
        ocap_id = create_response.json()["id"]
        
        client.post(f"/api/ocaps/{ocap_id}/executions", json={"status": "pending"})
        client.post(f"/api/ocaps/{ocap_id}/root-causes", json={"analysis_method": "5whys"})
        client.post(f"/api/ocaps/{ocap_id}/corrective-actions", json={"action_description": "测试措施"})
        
        delete_response = client.delete(f"/api/ocaps/{ocap_id}")
        assert delete_response.status_code == 200
        
        get_response = client.get(f"/api/ocaps/{ocap_id}")
        assert get_response.status_code == 404

    def test_ocap_nested_creation_complete(self, client):
        ocap_data = {
            "name": "嵌套创建完整测试",
            "description": "测试创建OCAP时同时创建Signal和Step",
            "signal_type": "trend_6",
            "priority": "critical",
            "status": "active",
            "signals": [
                {
                    "signal_time": "2026-03-07T09:00:00",
                    "signal_type": "trend_6",
                    "signal_value": "上升趋势",
                    "subgroup_index": 5
                },
                {
                    "signal_time": "2026-03-07T09:30:00",
                    "signal_type": "trend_6",
                    "signal_value": "持续上升趋势",
                    "subgroup_index": 10
                }
            ],
            "steps": [
                {
                    "phase": "containment",
                    "step_number": 1,
                    "action_type": "immediate",
                    "action_description": "立即停止生产",
                    "sort_order": 1
                },
                {
                    "phase": "investigation",
                    "step_number": 2,
                    "action_type": "short_term",
                    "action_description": "调查根本原因",
                    "prerequisites": [1],
                    "sort_order": 2
                },
                {
                    "phase": "correction",
                    "step_number": 3,
                    "action_type": "long_term",
                    "action_description": "实施纠正措施",
                    "prerequisites": [2],
                    "sort_order": 3
                }
            ]
        }
        
        response = client.post("/api/ocaps", json=ocap_data)
        assert response.status_code == 200
        data = response.json()
        
        assert len(data["signals"]) == 2
        assert len(data["steps"]) == 3
        assert data["steps"][0]["sort_order"] == 1
        assert data["steps"][1]["prerequisites"] == [1]
        assert data["steps"][2]["prerequisites"] == [2]


class TestOCAPDataValidation:
    
    def test_invalid_signal_type(self, client, sample_ocap):
        create_response = client.post("/api/ocaps", json=sample_ocap)
        ocap_id = create_response.json()["id"]
        
        invalid_signal = {
            "signal_type": "invalid_type"
        }
        response = client.post(f"/api/ocaps/{ocap_id}/signals", json=invalid_signal)
        assert response.status_code == 422

    def test_invalid_priority(self, client):
        invalid_ocap = {
            "name": "测试无效优先级",
            "priority": "invalid_priority"
        }
        response = client.post("/api/ocaps", json=invalid_ocap)
        assert response.status_code == 422

    def test_invalid_status(self, client):
        invalid_ocap = {
            "name": "测试无效状态",
            "status": "invalid_status"
        }
        response = client.post("/api/ocaps", json=invalid_ocap)
        assert response.status_code == 422

    def test_invalid_phase(self, client, sample_ocap):
        create_response = client.post("/api/ocaps", json=sample_ocap)
        ocap_id = create_response.json()["id"]
        
        invalid_step = {
            "phase": "invalid_phase"
        }
        response = client.post(f"/api/ocaps/{ocap_id}/steps", json=invalid_step)
        assert response.status_code == 422

    def test_score_range_validation(self, client):
        valid_ocap = {
            "name": "分数范围测试",
            "severity_score": 5,
            "scope_score": 5,
            "trend_score": 5
        }
        response = client.post("/api/ocaps", json=valid_ocap)
        assert response.status_code == 200
        data = response.json()
        assert data["severity_score"] == 5


class TestOCAPPerformance:
    
    def test_large_ocap_list(self, client):
        for i in range(50):
            ocap_data = {
                "name": f"性能测试OCAP-{i}",
                "priority": "medium",
                "status": "draft"
            }
            client.post("/api/ocaps", json=ocap_data)
        
        response = client.get("/api/ocaps")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 50

    def test_ocap_with_many_steps(self, client, sample_ocap):
        create_response = client.post("/api/ocaps", json=sample_ocap)
        ocap_id = create_response.json()["id"]
        
        for i in range(20):
            step_data = {
                "phase": "containment",
                "step_number": i + 1,
                "action_description": f"步骤{i + 1}",
                "sort_order": i + 1
            }
            client.post(f"/api/ocaps/{ocap_id}/steps", json=step_data)
        
        response = client.get(f"/api/ocaps/{ocap_id}/steps")
        assert response.status_code == 200
        assert len(response.json()) == 20

    def test_ocap_with_many_signals(self, client, sample_ocap):
        create_response = client.post("/api/ocaps", json=sample_ocap)
        ocap_id = create_response.json()["id"]
        
        for i in range(30):
            signal_data = {
                "signal_type": "point_beyond_3sigma",
                "signal_value": str(i),
                "subgroup_index": i
            }
            client.post(f"/api/ocaps/{ocap_id}/signals", json=signal_data)
        
        response = client.get(f"/api/ocaps/{ocap_id}/signals")
        assert response.status_code == 200
        assert len(response.json()) == 30
