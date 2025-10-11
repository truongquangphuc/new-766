"""
ZALO WEEKLY REPORT v1.4.1 - Fix: Lấy dữ liệu xã
Báo cáo DVC qua Zalo Bot - Fix step 7 lấy data xã/phường

Fix:
- Thêm error handling cho step 7
- Kiểm tra method tồn tại
- Log chi tiết để debug
- Workaround nếu không có API

Author: An Giang Province
Version: 1.4.1
Date: 2025-10-11
"""

import requests
import pandas as pd
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any


# ============================================================================
# CONFIGURATION
# ============================================================================

class ZaloReportConfig:
    """Cấu hình báo cáo Zalo"""

    # Zalo Bot Settings
    ZALO_BOT_TOKEN: str = "your-bot-token-here"
    ZALO_RECIPIENTS: List[str] = ["user_id_1"]

    # Province Settings
    PROVINCE_ID: str = "398126"
    PROVINCE_CODE: str = "398126"
    PROVINCE_NAME: str = "An Giang"

    # Export Settings
    EXPORT_EXCEL: bool = True
    EXPORT_DIR: Path = Path("./reports")

    # Display Settings
    NUM_INDICES: int = 7
    SHOW_RANKING: bool = True
    SHOW_TREND_MONTH: bool = True
    SHOW_TREND_QUARTER: bool = True
    SHOW_LOWEST_UNITS: bool = True
    NUM_LOWEST_UNITS: int = 5
    SHOW_LOWEST_COMMUNES: bool = True
    NUM_LOWEST_COMMUNES: int = 10

    def __post_init__(self):
        self.EXPORT_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================================
# MAIN CLASS
# ============================================================================

class ZaloWeeklyReport:
    """Tạo và gửi báo cáo DVC qua Zalo Bot"""

    def __init__(self, config: ZaloReportConfig = None):
        self.config = config or ZaloReportConfig()
        self.logger = self._setup_logger()
        self.data: Dict[str, Any] = {}
        self.api_url = f"https://bot-api.zapps.me/bot{self.config.ZALO_BOT_TOKEN}/sendMessage"
        self.config.EXPORT_DIR.mkdir(parents=True, exist_ok=True)

    def _setup_logger(self) -> logging.Logger:
        logger = logging.getLogger(self.__class__.__name__)
        logger.setLevel(logging.INFO)

        if not logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(
                logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            )
            logger.addHandler(handler)

        return logger

    def _get_period(self) -> Dict[str, Any]:
        now = datetime.now()
        return {
            "year": str(now.year),
            "month": now.month,
            "quarter": (now.month - 1) // 3 + 1,
            "week": now.isocalendar()[1],
            "date": now.strftime("%d/%m/%Y")
        }

    # ========================================================================
    # DATA FETCHING - FIX v1.4.1
    # ========================================================================

    def fetch_data(self) -> Dict[str, Any]:
        """
        Lấy dữ liệu từ DCV API

        Steps:
        1/7: Báo cáo năm
        2/7: Báo cáo tháng
        3/7: Chỉ số tháng
        4/7: Xu hướng 3 tháng
        5/7: Xu hướng quý
        6/7: Báo cáo Sở/Ban
        7/7: Báo cáo Xã/Phường ⭐ FIX
        """
        from dcv_api_client import DCVAPIClient

        self.logger.info("=" * 60)
        self.logger.info("BẮT ĐẦU LẤY DỮ LIỆU")
        self.logger.info("=" * 60)

        period = self._get_period()
        self.logger.info(f"Kỳ báo cáo: Tháng {period['month']}/{period['year']}, Quý {period['quarter']}")

        try:
            with DCVAPIClient() as client:
                # 1/7. Báo cáo 766 CẢ NĂM
                self.logger.info("1/7 Lấy báo cáo 766 cả năm...")
                report_766_year = client.get_tinh_766_report(
                    p_nam=period["year"],
                    p_tinh_id='0',
                    p_6thang=0,
                    p_quy=0,
                    p_thang=0
                )
                self.logger.info(f"    ✓ Số tỉnh: {len(report_766_year) if report_766_year else 0}")

                # 2/7. Báo cáo 766 THÁNG HIỆN TẠI
                self.logger.info(f"2/7 Lấy báo cáo 766 tháng {period['month']}...")
                report_766_month = client.get_tinh_766_report(
                    p_nam=period["year"],
                    p_tinh_id='0',
                    p_6thang=0,
                    p_quy=0,
                    p_thang=period["month"]
                )
                self.logger.info(f"    ✓ Số tỉnh: {len(report_766_month) if report_766_month else 0}")

                # 3/7. Chỉ số tháng hiện tại
                self.logger.info("3/7 Lấy chỉ số tháng...")
                indices = client.get_xuhuongdiem_chiso(
                    p_nam=period["year"],
                    p_tinh_id=self.config.PROVINCE_ID,
                    p_xa_id="0",
                    p_6thang=0,
                    p_quy=0,
                    p_thang=period["month"]
                )
                self.logger.info(f"    ✓ Số chỉ số: {len(indices) if indices else 0}")

                # 4/7. Xu hướng 3 THÁNG
                self.logger.info("4/7 Lấy xu hướng 3 tháng...")
                trend_months = self._fetch_trend_months(client, period["year"], period["month"])
                self.logger.info(f"    ✓ Số tháng: {len(trend_months)}")

                # 5/7. Xu hướng các QUÝ
                self.logger.info("5/7 Lấy xu hướng các quý...")
                trend_quarters = self._fetch_trend_quarters(client, period["year"], period["quarter"])
                self.logger.info(f"    ✓ Số quý: {len(trend_quarters)}")

                # 6/7. Báo cáo cấp SỞ/BAN
                self.logger.info("6/7 Lấy báo cáo cấp Sở/Ban...")
                try:
                    report_so_nganh = client.get_tinh_766_report_filtered(
                        p_nam=period["year"],
                        p_tinh_id=self.config.PROVINCE_CODE,
                        p_6thang=0,
                        p_quy=0,
                        p_thang=period["month"],
                        capdonviid="1"
                    )
                    self.logger.info(f"    ✓ Số Sở/Ban: {len(report_so_nganh) if report_so_nganh else 0}")
                except Exception as e:
                    self.logger.error(f"    ✗ Lỗi lấy Sở/Ban: {e}")
                    report_so_nganh = []

                # 7/7. Báo cáo cấp XÃ/PHƯỜNG ⭐ FIX
                self.logger.info("7/7 Lấy báo cáo cấp Xã/Phường...")
                report_xa = []

                try:
                    if hasattr(client, 'get_tinh_766_report_filtered'):
                        self.logger.info("    → Gọi API get_tinh_766_report_filtered...")
                        report_xa = client.get_tinh_766_report_filtered(
                            p_nam=period["year"],
                            p_tinh_id=self.config.PROVINCE_CODE,
                            p_6thang=0,
                            p_quy=0,
                            p_thang=period["month"],
                            capdonviid="2"
                        )
                        self.logger.info(f"    ✓ Số Xã: {len(report_xa) if report_xa else 0}")
                    else:
                        self.logger.warning("    ⚠️  Method get_tinh_766_report_filtered không tồn tại!")
                        self.logger.warning("    → Thử workaround...")

                        if hasattr(client, 'get_huyen_xa_766_report'):
                            report_xa = client.get_huyen_xa_766_report(
                                p_nam=period["year"],
                                p_tinh_id=self.config.PROVINCE_CODE,
                                p_6thang=0,
                                p_quy=0,
                                p_thang=period["month"]
                            )
                            self.logger.info(f"    ✓ Số Xã (workaround): {len(report_xa) if report_xa else 0}")
                        else:
                            self.logger.error("    ✗ Không có method nào để lấy data Xã!")

                except AttributeError as e:
                    self.logger.error(f"    ✗ AttributeError: {e}")
                    self.logger.error(f"    → Method không tồn tại trong DCVAPIClient")

                except Exception as e:
                    self.logger.error(f"    ✗ Lỗi lấy Xã: {e}")
                    self.logger.error(f"    → Type: {type(e).__name__}")
                    import traceback
                    self.logger.error(f"    → Traceback:\n{traceback.format_exc()}")

                # Log tổng kết
                self.logger.info("")
                self.logger.info("TỔNG KẾT DỮ LIỆU:")
                self.logger.info(f"  - Báo cáo năm: {len(report_766_year) if report_766_year else 0} tỉnh")
                self.logger.info(f"  - Báo cáo tháng: {len(report_766_month) if report_766_month else 0} tỉnh")
                self.logger.info(f"  - Chỉ số: {len(indices) if indices else 0} chỉ số")
                self.logger.info(f"  - Xu hướng tháng: {len(trend_months)} tháng")
                self.logger.info(f"  - Xu hướng quý: {len(trend_quarters)} quý")
                self.logger.info(f"  - Sở/Ban: {len(report_so_nganh) if report_so_nganh else 0} đơn vị")
                self.logger.info(f"  - Xã: {len(report_xa) if report_xa else 0} đơn vị")

                # Lưu data
                self.data = {
                    "period": period,
                    "report_tinh_766_year": report_766_year,
                    "report_tinh_766_month": report_766_month,
                    "chiso": indices,
                    "trend_months": trend_months,
                    "trend_quarters": trend_quarters,
                    "report_so_nganh": report_so_nganh,
                    "report_xa": report_xa
                }

                self.logger.info("=" * 60)
                self.logger.info("✅ LẤY DỮ LIỆU THÀNH CÔNG")
                self.logger.info("=" * 60)

                return self.data

        except Exception as e:
            self.logger.error(f"❌ LỖI TỔNG THỂ: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
            raise

    def _fetch_trend_months(self, client, year: str, current_month: int) -> List[Dict]:
        """Lấy xu hướng 3 tháng gần nhất"""
        trends = []

        for i in range(2, -1, -1):
            month = current_month - i
            year_to_use = year

            if month < 1:
                month += 12
                year_to_use = str(int(year) - 1)

            try:
                self.logger.info(f"       Tháng {month}/{year_to_use}...")

                report = client.get_tinh_766_report(
                    p_nam=year_to_use,
                    p_tinh_id='0',
                    p_6thang=0,
                    p_quy=0,
                    p_thang=month
                )

                if report:
                    filtered = [item for item in report 
                               if item.get("ID") == self.config.PROVINCE_ID]

                    if filtered:
                        score = filtered[0].get('TONG_SCORE', 'N/A')
                        try:
                            score = round(float(score), 1) if score != 'N/A' else 'N/A'
                        except:
                            score = 'N/A'

                        trends.append({
                            "month": month,
                            "year": year_to_use,
                            "score": score
                        })
                        self.logger.info(f"          ✓ {score}")

            except Exception as e:
                self.logger.warning(f"          ✗ Lỗi: {e}")

        return trends

    def _fetch_trend_quarters(self, client, year: str, current_quarter: int) -> List[Dict]:
        """Lấy xu hướng các quý"""
        trends = []

        for q in range(1, current_quarter + 1):
            try:
                self.logger.info(f"       Quý {q}...")

                report = client.get_tinh_766_report(
                    p_nam=year,
                    p_tinh_id='0',
                    p_6thang=0,
                    p_quy=q,
                    p_thang=0
                )

                if report:
                    filtered = [item for item in report 
                               if item.get("ID") == self.config.PROVINCE_ID]

                    if filtered:
                        score = filtered[0].get('TONG_SCORE', 'N/A')
                        try:
                            score = round(float(score), 1) if score != 'N/A' else 'N/A'
                        except:
                            score = 'N/A'

                        trends.append({
                            "quarter": q,
                            "year": year,
                            "score": score
                        })
                        self.logger.info(f"          ✓ Q{q}: {score}")

            except Exception as e:
                self.logger.warning(f"          ✗ Lỗi Q{q}: {e}")

        return trends

    # ========================================================================
    # DATA PROCESSING
    # ========================================================================

    def _get_province_report(self, period_type: str = 'year') -> Optional[Dict[str, Any]]:
        """Lấy thông tin tỉnh từ report"""
        if period_type == 'year':
            report_data = self.data.get('report_tinh_766_year', [])
        else:
            report_data = self.data.get('report_tinh_766_month', [])

        if not report_data:
            return None

        filtered = [item for item in report_data 
                   if item.get("ID") == self.config.PROVINCE_ID]

        return filtered[0] if filtered else None

    def _get_lowest_5_units(self) -> List[Dict[str, Any]]:
        """Lấy 5 đơn vị Sở/Ban có kết quả thấp nhất"""
        report_so_nganh = self.data.get('report_so_nganh', [])

        if not report_so_nganh:
            return []

        sorted_units = sorted(
            report_so_nganh,
            key=lambda x: float(x.get('TONG_SCORE', 0))
        )

        lowest_5 = sorted_units[:self.config.NUM_LOWEST_UNITS]

        result = []
        total = len(sorted_units)

        for idx, unit in enumerate(lowest_5, 1):
            result.append({
                "name": unit.get('TEN', 'N/A'),
                "score": float(unit.get('TONG_SCORE', 0)),
                "rank": idx,
                "total": total
            })

        return result

    def _get_lowest_10_communes(self) -> List[Dict[str, Any]]:
        """Lấy 10 xã/phường có kết quả thấp nhất"""
        report_xa = self.data.get('report_xa', [])

        if not report_xa:
            return []

        sorted_communes = sorted(
            report_xa,
            key=lambda x: float(x.get('TONG_SCORE', 0))
        )

        lowest_10 = sorted_communes[:self.config.NUM_LOWEST_COMMUNES]

        result = []
        total = len(sorted_communes)

        for idx, commune in enumerate(lowest_10, 1):
            result.append({
                "name": commune.get('TEN', 'N/A'),
                "score": float(commune.get('TONG_SCORE', 0)),
                "rank": idx,
                "total": total
            })

        return result

    # ========================================================================
    # MESSAGE FORMATTING
    # ========================================================================

    def format_message(self) -> str:
        """Format tin nhắn đầy đủ"""
        p = self.data.get("period", {})

        province_year = self._get_province_report('year')
        province_month = self._get_province_report('month')

        indices = self.data.get("chiso", [])
        trend_months = self.data.get("trend_months", [])
        trend_quarters = self.data.get("trend_quarters", [])
        lowest_units = self._get_lowest_5_units()
        lowest_communes = self._get_lowest_10_communes()

        lines = [
            f"📊 BÁO CÁO DVC - {self.config.PROVINCE_NAME.upper()}",
            "━━━━━━━━━━━━━━━━━━━━",
            f"📅 Ngày {p.get('date')}",
            ""
        ]

        # 1. ĐIỂM NĂM
        lines.append(f"━━━ ĐIỂM NĂM {p.get('year')} ━━━")

        if province_year:
            year_score = province_year.get('TONG_SCORE', 'N/A')
            year_rank = province_year.get('ROW_STT', 'N/A')
            total = len(self.data.get('report_tinh_766_year', []))

            lines.append(f"🎯 Điểm: {year_score}/100")
            if self.config.SHOW_RANKING:
                lines.append(f"🏆 Hạng: {year_rank}/{total}")
        else:
            lines.append("🎯 Điểm: N/A")

        lines.append("")

        # 2. ĐIỂM THÁNG
        lines.append(f"━━━ ĐIỂM THÁNG {p.get('month')}/{p.get('year')} ━━━")

        if province_month:
            month_score = province_month.get('TONG_SCORE', 'N/A')
            month_rank = province_month.get('ROW_STT', 'N/A')
            total = len(self.data.get('report_tinh_766_month', []))

            lines.append(f"🎯 Điểm: {month_score}/100")
            if self.config.SHOW_RANKING:
                lines.append(f"🏆 Hạng: {month_rank}/{total}")
        else:
            lines.append("🎯 Điểm: N/A")

        lines.append("")

        # 3. CHỈ SỐ
        if indices:
            lines.append("📊 CHỈ SỐ:")

            display_count = min(self.config.NUM_INDICES, len(indices))
            for idx in indices[:display_count]:
                code = idx.get('CODE', '')
                score = float(idx.get('SCORE', 0))
                max_score = float(idx.get('MAX_SCORE', 1))

                score_pct = (score / max_score * 100) if max_score > 0 else 0

                if score_pct >= 90:
                    icon = "🌟"
                elif score_pct >= 80:
                    icon = "✅"
                elif score_pct >= 70:
                    icon = "⚠️"
                else:
                    icon = "❌"

                lines.append(f"{icon} {code}: {score:.1f}/{max_score:.0f} ({score_pct:.1f}%)")

            lines.append("")

        # 4. XU HƯỚNG 3 THÁNG
        if self.config.SHOW_TREND_MONTH and trend_months and len(trend_months) >= 2:
            lines.append("━━━ XU HƯỚNG 3 THÁNG ━━━")

            for t in trend_months:
                score = t['score']
                if score != 'N/A':
                    lines.append(f"Tháng {t['month']:02d}: {score}/100")
                else:
                    lines.append(f"Tháng {t['month']:02d}: N/A")

            valid = [t for t in trend_months if t['score'] != 'N/A']
            if len(valid) >= 2:
                first = float(valid[0]['score'])
                last = float(valid[-1]['score'])
                change = last - first

                if change > 0:
                    icon, text = "📈", f"+{change:.1f}"
                elif change < 0:
                    icon, text = "📉", f"{change:.1f}"
                else:
                    icon, text = "➡️", "0"

                lines.append(f"\n{icon} Biến động: {text} điểm")

            lines.append("")

        # 5. XU HƯỚNG QUÝ
        if self.config.SHOW_TREND_QUARTER and trend_quarters and len(trend_quarters) >= 1:
            lines.append("━━━ XU HƯỚNG CÁC QUÝ ━━━")

            for t in trend_quarters:
                score = t['score']
                if score != 'N/A':
                    lines.append(f"Quý {t['quarter']}: {score}/100")
                else:
                    lines.append(f"Quý {t['quarter']}: N/A")

            valid = [t for t in trend_quarters if t['score'] != 'N/A']
            if len(valid) >= 2:
                first = float(valid[0]['score'])
                last = float(valid[-1]['score'])
                change = last - first

                if change > 0:
                    icon, text = "📈", f"+{change:.1f}"
                elif change < 0:
                    icon, text = "📉", f"{change:.1f}"
                else:
                    icon, text = "➡️", "0"

                lines.append(f"\n{icon} Biến động: {text} điểm")

            lines.append("")

        # 6. 5 SỞ/BAN THẤP NHẤT
        if self.config.SHOW_LOWEST_UNITS and lowest_units:
            lines.append("━━━ ⚠️ 5 SỞ/BAN CẦN CẢI THIỆN ━━━")

            for unit in lowest_units:
                name = unit['name']
                if len(name) > 30:
                    name = name[:27] + "..."

                lines.append(f"{unit['rank']}. {name}")
                lines.append(f"   Điểm: {unit['score']:.1f}/100")

            lines.append("")

        # 7. 10 XÃ THẤP NHẤT
        if self.config.SHOW_LOWEST_COMMUNES and lowest_communes:
            lines.append("━━━ ⚠️ 10 XÃ/PHƯỜNG CẦN CẢI THIỆN ━━━")

            for commune in lowest_communes:
                name = commune['name']
                if len(name) > 35:
                    name = name[:32] + "..."

                lines.append(f"{commune['rank']}. {name}")
                lines.append(f"   Điểm: {commune['score']:.1f}/100")

            lines.append("")

        lines.extend([
            "━━━━━━━━━━━━━━━━━━━━",
            f"🏛️ Sở Khoa học & Công nghệ {self.config.PROVINCE_NAME}",
            "🤖 Báo cáo tự động từ Zalo Bot"
        ])

        message = "\n".join(lines)

        if len(message) > 2000:
            message = message[:1980] + "\n...\n(Đã rút gọn)"
            self.logger.warning("Tin nhắn quá dài, đã cắt")

        return message

    # ========================================================================
    # SENDING & EXPORT & RUN (giống v1.4.0)
    # ========================================================================

    def send_zalo(self, message: str) -> List[Dict[str, Any]]:
        """Gửi tin nhắn qua Zalo"""
        self.logger.info("=" * 60)
        self.logger.info("GỬI ZALO")
        self.logger.info("=" * 60)

        results = []

        for idx, chat_id in enumerate(self.config.ZALO_RECIPIENTS, 1):
            try:
                self.logger.info(f"{idx}/{len(self.config.ZALO_RECIPIENTS)}: {chat_id}")

                response = requests.post(
                    self.api_url,
                    json={"chat_id": chat_id, "text": message},
                    timeout=30
                )
                response.raise_for_status()
                result = response.json()

                if result.get("ok"):
                    msg_id = result.get('result', {}).get('message_id', 'N/A')
                    self.logger.info(f"   ✓ OK! ID: {msg_id}")
                    results.append({"chat_id": chat_id, "ok": True, "message_id": msg_id})
                else:
                    self.logger.error(f"   ✗ Failed: {result}")
                    results.append({"chat_id": chat_id, "ok": False, "error": result})

            except Exception as e:
                self.logger.error(f"   ✗ Error: {e}")
                results.append({"chat_id": chat_id, "ok": False, "error": str(e)})

        success = sum(1 for r in results if r.get("ok"))
        self.logger.info(f"Result: {success}/{len(results)}")

        return results

    def export_excel(self) -> Optional[Path]:
        """Export Excel"""
        if not self.config.EXPORT_EXCEL:
            return None

        p = self.data.get("period", {})
        filename = f"bao_cao_T{p.get('month'):02d}_{p.get('year')}.xlsx"
        filepath = self.config.EXPORT_DIR / filename

        try:
            self.logger.info(f"Export: {filepath}")

            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                if self.data.get("report_tinh_766_year"):
                    pd.DataFrame(self.data["report_tinh_766_year"]).to_excel(
                        writer, sheet_name="Điểm năm", index=False
                    )

                if self.data.get("report_tinh_766_month"):
                    pd.DataFrame(self.data["report_tinh_766_month"]).to_excel(
                        writer, sheet_name="Điểm tháng", index=False
                    )

                if self.data.get("chiso"):
                    pd.DataFrame(self.data["chiso"]).to_excel(
                        writer, sheet_name="Chỉ số", index=False
                    )

                if self.data.get("trend_months"):
                    pd.DataFrame(self.data["trend_months"]).to_excel(
                        writer, sheet_name="Xu hướng tháng", index=False
                    )

                if self.data.get("trend_quarters"):
                    pd.DataFrame(self.data["trend_quarters"]).to_excel(
                        writer, sheet_name="Xu hướng quý", index=False
                    )

                if self.data.get("report_so_nganh"):
                    pd.DataFrame(self.data["report_so_nganh"]).to_excel(
                        writer, sheet_name="Sở Ban", index=False
                    )

                if self.data.get("report_xa"):
                    pd.DataFrame(self.data["report_xa"]).to_excel(
                        writer, sheet_name="Xã Phường", index=False
                    )

            self.logger.info("   ✓ OK")
            return filepath

        except Exception as e:
            self.logger.error(f"   ✗ Error: {e}")
            return None

    def run(self, preview_only: bool = False) -> Dict[str, Any]:
        """Chạy toàn bộ"""
        self.logger.info("\n" + "=" * 60)
        self.logger.info("ZALO WEEKLY REPORT v1.4.1")
        self.logger.info("=" * 60)

        try:
            self.fetch_data()
            message = self.format_message()

            print("\n" + "=" * 60)
            print("PREVIEW:")
            print("=" * 60)
            print(message)
            print("=" * 60)
            print(f"Length: {len(message)} chars")
            print("=" * 60)

            if preview_only:
                self.logger.info("\n📋 PREVIEW ONLY")
                return {
                    "success": True,
                    "preview_only": True,
                    "message": message
                }

            results = self.send_zalo(message)
            excel = self.export_excel()

            success_count = sum(1 for r in results if r.get("ok"))

            self.logger.info("\n" + "=" * 60)
            self.logger.info("✅ DONE")
            self.logger.info(f"Sent: {success_count}/{len(results)}")
            if excel:
                self.logger.info(f"Excel: {excel}")
            self.logger.info("=" * 60)

            return {
                "success": success_count == len(results),
                "sent": success_count,
                "total": len(results),
                "excel": excel,
                "message": message,
                "details": results
            }

        except Exception as e:
            self.logger.error(f"\n❌ ERROR: {e}")
            import traceback
            traceback.print_exc()
            raise


def schedule_monthly():
    """Schedule tự động"""
    import schedule
    import time

    def job():
        if datetime.now().day != 1:
            return

        print("\n" + "=" * 60)
        print("AUTO RUN")
        print("=" * 60)

        try:
            config = ZaloReportConfig()
            report = ZaloWeeklyReport(config)
            report.run()
        except Exception as e:
            print(f"❌ Error: {e}")

    schedule.every().day.at("08:00").do(job)

    print("📅 Scheduler ON")
    print("⏰ Run 1st day, 8AM")
    print("Ctrl+C to stop...\n")

    while True:
        schedule.run_pending()
        time.sleep(3600)


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    import sys

    config = ZaloReportConfig()
    config.ZALO_BOT_TOKEN = "430881819486503765:SmZoEoNvmeMlIoGEchwbUvTKufwSPjvTtRooeThVbpixRwjwIvwrLuIMbOOrHDkU"
    config.ZALO_RECIPIENTS = ["7aefa72bcd63243d7d72"]
    config.PROVINCE_ID = "398126"
    config.PROVINCE_CODE = "398126"
    config.PROVINCE_NAME = "An Giang"

    preview_only = len(sys.argv) > 1 and sys.argv[1] == "preview"

    report = ZaloWeeklyReport(config)
    result = report.run(preview_only=preview_only)

    if result.get("success"):
        print("\n✅ SUCCESS!")
    else:
        print("\n⚠️  PARTIAL FAILURE")