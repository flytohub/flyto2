"""
Strict PR Reviewer - 嚴格的程式碼品質評分系統
針對 Flyto2 Production Atomic Modules 的高標準審查
"""
from pathlib import Path
from typing import Dict, List, Tuple
import re


class StrictPRReviewer:
    """嚴格的 PR 審查系統，符合 Flyto2 生產級標準"""

    def __init__(self):
        self.issues = []
        self.score = 10.0

    def review_module(self, file_path: str) -> Dict:
        """
        審查模組程式碼

        Returns:
            {
                "score": float,  # 0-10
                "grade": str,    # A+, A, B, C, D, F
                "issues": List[Dict],
                "strengths": List[str],
                "recommendations": List[str]
            }
        """
        self.issues = []
        self.score = 10.0
        self.strengths = []
        self.recommendations = []

        # 讀取檔案
        content = Path(file_path).read_text()
        lines = content.split('\n')

        # === 基本檢查 (舊系統) ===
        self._check_basic_quality(content, lines)

        # === 進階檢查 (新增) ===
        self._check_duplicate_imports(content)
        self._check_security(content, file_path)
        self._check_error_handling_quality(content)
        self._check_input_validation(content, file_path)
        self._check_streaming_download(content, file_path)
        self._check_return_format(content)
        self._check_module_specific(content, file_path)

        # 計算等級
        grade = self._calculate_grade(self.score)

        # 生成建議
        if self.score < 9.8:
            self._generate_recommendations()

        return {
            "score": round(self.score, 1),
            "grade": grade,
            "issues": self.issues,
            "strengths": self.strengths,
            "recommendations": self.recommendations,
            "pass": self.score >= 9.8
        }

    def _check_basic_quality(self, content: str, lines: List[str]):
        """基本品質檢查"""
        # Docstring
        if '"""' in content or "'''" in content:
            self.strengths.append("✅ 包含完整 docstring")
        else:
            self._add_issue("缺少 docstring", severity="high", deduction=1.0)

        # Type hints
        if '->' in content and (': str' in content or ': int' in content or ': Dict' in content):
            self.strengths.append("✅ 包含 type hints")
        else:
            self._add_issue("缺少 type hints", severity="medium", deduction=0.5)

        # Error handling
        if 'try:' in content and 'except' in content:
            self.strengths.append("✅ 包含錯誤處理")
        else:
            self._add_issue("缺少錯誤處理", severity="critical", deduction=2.0)

        # Validation
        if 'if not' in content or 'raise ValueError' in content:
            self.strengths.append("✅ 包含參數驗證")
        else:
            self._add_issue("缺少參數驗證", severity="high", deduction=1.0)

    def _check_duplicate_imports(self, content: str):
        """檢查重複 import（LLM 常見問題）"""
        # 找出所有 import 語句
        top_imports = re.findall(r'^(?:from|import)\s+[\w.]+', content, re.MULTILINE)
        function_imports = re.findall(r'^\s{4,}(?:from|import)\s+[\w.]+', content, re.MULTILINE)

        if function_imports:
            duplicates = []
            for func_import in function_imports:
                module = func_import.strip().split()[1]
                for top_import in top_imports:
                    if module in top_import:
                        duplicates.append(module)

            if duplicates:
                self._add_issue(
                    f"函數內重複 import: {', '.join(set(duplicates))}",
                    severity="medium",
                    deduction=0.5,
                    suggestion="將 import 移到檔案開頭"
                )
        else:
            self.strengths.append("✅ 無重複 import")

    def _check_security(self, content: str, file_path: str):
        """安全性檢查"""
        issues_found = []

        # 檢查 Content-Type 驗證（針對下載模組）
        if 'download' in file_path.lower() or 'fetch' in file_path.lower():
            if 'content-type' not in content.lower() and 'content_type' not in content:
                self._add_issue(
                    "缺少 Content-Type 驗證（安全風險）",
                    severity="critical",
                    deduction=1.5,
                    suggestion="檢查 response.headers['content-type'] 是否為預期格式"
                )
                issues_found.append("content-type")

        # 檢查檔案大小限制
        if 'download' in file_path.lower() or 'response.content' in content:
            if 'content-length' not in content.lower() and 'len(' not in content:
                self._add_issue(
                    "缺少檔案大小限制（記憶體風險）",
                    severity="high",
                    deduction=1.0,
                    suggestion="檢查 Content-Length 或設定最大下載大小"
                )
                issues_found.append("size-limit")

        # 檢查 URL 驗證
        if 'self.url' in content or 'url' in content.lower():
            if 'startswith("http' not in content and 'urlparse' not in content:
                self._add_issue(
                    "缺少 URL 格式驗證",
                    severity="medium",
                    deduction=0.5,
                    suggestion="驗證 URL 必須是 http:// 或 https://"
                )
                issues_found.append("url-validation")

        # 危險操作檢查
        dangerous = [
            ('os.system', '使用危險的 os.system'),
            ('eval(', '使用危險的 eval'),
            ('exec(', '使用危險的 exec'),
        ]

        for pattern, desc in dangerous:
            if pattern in content:
                self._add_issue(desc, severity="critical", deduction=3.0)
                issues_found.append(pattern)

        if not issues_found:
            self.strengths.append("✅ 通過安全性檢查")

    def _check_error_handling_quality(self, content: str):
        """檢查錯誤處理的品質"""
        # 檢查是否有 bare except（不好的做法）
        if re.search(r'except\s*:', content):
            self._add_issue(
                "使用 bare except（不推薦）",
                severity="low",
                deduction=0.3,
                suggestion="明確指定 Exception 類型"
            )
        else:
            self.strengths.append("✅ 錯誤處理明確具體")

        # 檢查是否有多層錯誤處理
        except_count = content.count('except ')
        if except_count >= 3:
            self.strengths.append(f"✅ 多層錯誤處理 ({except_count} 個)")

    def _check_input_validation(self, content: str, file_path: str):
        """檢查輸入驗證的完整性"""
        # 檢查是否有 validate_params
        if 'def validate_params' not in content:
            self._add_issue(
                "缺少 validate_params 方法",
                severity="critical",
                deduction=2.0
            )
            return

        # 檢查驗證的深度
        has_type_check = 'isinstance(' in content
        has_range_check = any(x in content for x in ['if ', '< ', '> ', '<=', '>='])
        has_format_check = 'match' in content or 're.' in content

        validation_depth = sum([has_type_check, has_range_check, has_format_check])

        if validation_depth == 0:
            self._add_issue(
                "參數驗證過於簡單",
                severity="medium",
                deduction=0.5,
                suggestion="增加類型、範圍或格式檢查"
            )

    def _check_streaming_download(self, content: str, file_path: str):
        """檢查是否使用 streaming 下載（針對下載模組）"""
        if 'download' not in file_path.lower():
            return

        # 檢查是否直接使用 response.content（不好）
        if 'response.content' in content:
            # 檢查是否有 streaming 或 chunk
            if 'stream=' not in content and 'iter_content' not in content and 'iter_bytes' not in content:
                self._add_issue(
                    "使用 response.content 而非 streaming（記憶體效率低）",
                    severity="medium",
                    deduction=0.8,
                    suggestion="使用 stream=True 和 iter_bytes/iter_content"
                )
            else:
                self.strengths.append("✅ 使用 streaming 下載")

    def _check_return_format(self, content: str):
        """檢查回傳格式是否符合 Flyto2 規範"""
        # 檢查是否有統一的回傳格式
        returns = re.findall(r'return\s+\{[^}]+\}', content, re.DOTALL)

        if not returns:
            return

        # 檢查所有 return 是否都有 "status" 欄位
        has_status = all('status' in r for r in returns)

        if has_status:
            self.strengths.append("✅ 統一的回傳格式 (包含 status)")
        else:
            self._add_issue(
                "回傳格式不一致",
                severity="low",
                deduction=0.3,
                suggestion="所有回傳都應包含 'status' 欄位"
            )

    def _check_module_specific(self, content: str, file_path: str):
        """模組特定檢查"""
        # 檢查是否有嵌套函數定義（不好）
        nested_def_pattern = r'^\s{8,}(?:async\s+)?def\s+\w+'
        nested_defs = re.findall(nested_def_pattern, content, re.MULTILINE)

        if nested_defs:
            self._add_issue(
                f"包含嵌套函數定義 ({len(nested_defs)} 個)",
                severity="high",
                deduction=1.5,
                suggestion="將嵌套函數提取為獨立方法"
            )
        else:
            self.strengths.append("✅ 無嵌套函數定義")

        # 檢查程式碼長度
        code_lines = [l for l in content.split('\n') if l.strip() and not l.strip().startswith('#')]

        if len(code_lines) < 20:
            self._add_issue(
                "程式碼過短，可能不完整",
                severity="high",
                deduction=1.0
            )
        elif len(code_lines) > 200:
            self._add_issue(
                "程式碼過長，建議拆分",
                severity="low",
                deduction=0.3
            )
        else:
            self.strengths.append(f"✅ 程式碼長度適中 ({len(code_lines)} 行)")

    def _add_issue(self, message: str, severity: str, deduction: float, suggestion: str = ""):
        """新增問題"""
        self.issues.append({
            "message": message,
            "severity": severity,
            "deduction": deduction,
            "suggestion": suggestion
        })
        self.score -= deduction
        self.score = max(0.0, self.score)  # 不低於 0

    def _calculate_grade(self, score: float) -> str:
        """計算等級"""
        if score >= 9.8:
            return "A+"
        elif score >= 9.5:
            return "A"
        elif score >= 9.0:
            return "A-"
        elif score >= 8.5:
            return "B+"
        elif score >= 8.0:
            return "B"
        elif score >= 7.5:
            return "B-"
        elif score >= 7.0:
            return "C+"
        elif score >= 6.5:
            return "C"
        elif score >= 6.0:
            return "C-"
        else:
            return "F"

    def _generate_recommendations(self):
        """生成改進建議"""
        if self.score < 9.8:
            self.recommendations.append("🎯 目標: 達到 9.8/10 (A+ 等級)")

        # 根據問題生成建議
        critical_issues = [i for i in self.issues if i['severity'] == 'critical']
        high_issues = [i for i in self.issues if i['severity'] == 'high']

        if critical_issues:
            self.recommendations.append(f"⚠️  優先修復 {len(critical_issues)} 個嚴重問題")

        if high_issues:
            self.recommendations.append(f"⚠️  修復 {len(high_issues)} 個高優先級問題")

        # 如果接近目標，給具體建議
        if 9.0 <= self.score < 9.8:
            remaining = 9.8 - self.score
            self.recommendations.append(f"💡 還差 {remaining:.1f} 分達到目標，專注修復上述問題")


def review_module_file(file_path: str) -> Dict:
    """審查單一模組檔案"""
    reviewer = StrictPRReviewer()
    return reviewer.review_module(file_path)


if __name__ == "__main__":
    # 測試
    result = review_module_file("src/core/modules/atomic/image/download.py")

    print("=" * 80)
    print(f"📊 PR 審查結果")
    print("=" * 80)
    print(f"評分: {result['score']}/10.0 ({result['grade']})")
    print(f"是否通過: {'✅ PASS' if result['pass'] else '❌ FAIL'}")
    print()

    if result['strengths']:
        print("✅ 優點:")
        for s in result['strengths']:
            print(f"  {s}")
        print()

    if result['issues']:
        print("❌ 問題:")
        for i in result['issues']:
            print(f"  [{i['severity'].upper()}] {i['message']} (-{i['deduction']})")
            if i['suggestion']:
                print(f"      💡 {i['suggestion']}")
        print()

    if result['recommendations']:
        print("📋 改進建議:")
        for r in result['recommendations']:
            print(f"  {r}")
