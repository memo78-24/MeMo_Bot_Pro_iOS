#!/usr/bin/env python3
"""
Generate MeMo Bot Pro System Status Report PDF
"""

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from datetime import datetime

def create_system_report():
    """Generate the system status report PDF"""
    
    # Create PDF document
    filename = "MeMo_Bot_Pro_System_Status_Report.pdf"
    doc = SimpleDocTemplate(filename, pagesize=A4,
                           rightMargin=72, leftMargin=72,
                           topMargin=72, bottomMargin=18)
    
    # Container for the 'Flowable' objects
    elements = []
    
    # Define styles
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#667eea'),
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#333333'),
        spaceAfter=12,
        spaceBefore=12,
        fontName='Helvetica-Bold'
    )
    
    subheading_style = ParagraphStyle(
        'CustomSubHeading',
        parent=styles['Heading3'],
        fontSize=14,
        textColor=colors.HexColor('#555555'),
        spaceAfter=10,
        spaceBefore=10,
        fontName='Helvetica-Bold'
    )
    
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['BodyText'],
        fontSize=11,
        textColor=colors.HexColor('#333333'),
        spaceAfter=6,
        fontName='Helvetica'
    )
    
    # Title
    elements.append(Paragraph("🤖 MeMo Bot Pro", title_style))
    elements.append(Paragraph("System Status Report", title_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # Report info
    report_date = datetime.now().strftime("%B %d, %Y at %H:%M UTC")
    elements.append(Paragraph(f"<i>Generated: {report_date}</i>", body_style))
    elements.append(Spacer(1, 0.3*inch))
    
    # === ENGLISH SECTION ===
    elements.append(Paragraph("📊 ENGLISH SUMMARY", heading_style))
    elements.append(Spacer(1, 0.1*inch))
    
    # Overall Status
    elements.append(Paragraph("✅ All Systems Working Perfectly!", subheading_style))
    elements.append(Paragraph(
        "Your screenshots show the <b>MeMo Bot Pro</b> dashboard tracking live cryptocurrency "
        "prices over 4 minutes (from 06:56 to 07:00 UTC). The system is fully operational.",
        body_style
    ))
    elements.append(Spacer(1, 0.15*inch))
    
    # 1. Live Price Updates
    elements.append(Paragraph("1️⃣ Live Price Updates Working 📈", subheading_style))
    elements.append(Paragraph(
        "The system is successfully pulling <b>real-time data</b> from Binance API. "
        "Prices are updating continuously every 30 seconds:",
        body_style
    ))
    
    price_data = [
        ['Currency', 'Price Range', 'Status'],
        ['BTC', '$103,354 - $103,391', '✅ Live'],
        ['ETH', '$3,438 - $3,442', '✅ Live'],
        ['XRP', '$2.38 - $2.39', '✅ Live'],
    ]
    
    price_table = Table(price_data, colWidths=[2*inch, 2*inch, 1.5*inch])
    price_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    elements.append(Spacer(1, 0.1*inch))
    elements.append(price_table)
    elements.append(Paragraph(
        "<i>These are <b>genuine live prices</b>, not simulated data!</i>",
        body_style
    ))
    elements.append(Spacer(1, 0.15*inch))
    
    # 2. All 10 Currencies
    elements.append(Paragraph("2️⃣ Dashboard Displaying All 10 Currencies ✅", subheading_style))
    elements.append(Paragraph(
        "Successfully showing the top 10 cryptocurrencies:",
        body_style
    ))
    
    crypto_list = """
    1. BTCUSDT (Bitcoin)<br/>
    2. ETHUSDT (Ethereum)<br/>
    3. BNBUSDT (Binance Coin)<br/>
    4. LTCUSDT (Litecoin)<br/>
    5. ADAUSDT (Cardano)<br/>
    6. XRPUSDT (Ripple)<br/>
    7. MATICUSDT (Polygon)<br/>
    8. DOGEUSDT (Dogecoin)<br/>
    9. SOLUSDT (Solana)<br/>
    10. DOTUSDT (Polkadot)
    """
    elements.append(Paragraph(crypto_list, body_style))
    elements.append(Spacer(1, 0.15*inch))
    
    # 3. Health Monitor
    elements.append(Paragraph("3️⃣ Health Monitor Status 🏥", subheading_style))
    
    health_data = [
        ['Component', 'Status', 'Details'],
        ['Binance API', '✅ Connected', 'Live Mode'],
        ['Telegram Bot', '✅ Connected', '1 Admin'],
        ['Configuration', '✅ Valid', 'All credentials set'],
        ['System Resources', '✅ Healthy', 'CPU/Memory normal'],
    ]
    
    health_table = Table(health_data, colWidths=[2*inch, 1.5*inch, 2*inch])
    health_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#10b981')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.lightgreen),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    elements.append(health_table)
    elements.append(Spacer(1, 0.15*inch))
    
    # 4. Notifications Ready
    elements.append(Paragraph("4️⃣ Ready for Notifications 🔔", subheading_style))
    elements.append(Paragraph(
        "The Telegram bot is actively monitoring these 10 currencies. When any price changes by "
        "<b>1% or more</b>, your <b>2 subscribed users</b> will receive instant alerts in Arabic!",
        body_style
    ))
    elements.append(Spacer(1, 0.2*inch))
    
    # Key Features
    elements.append(Paragraph("🎯 Key Features Confirmed", subheading_style))
    features_list = """
    ✅ Real-time price tracking from Binance<br/>
    ✅ All 10 top cryptocurrencies displayed<br/>
    ✅ Health monitoring system operational<br/>
    ✅ Telegram bot connected and monitoring<br/>
    ✅ 2 users subscribed for Arabic notifications<br/>
    ✅ 1% price change threshold configured<br/>
    ✅ 5-minute cooldown per symbol to prevent spam
    """
    elements.append(Paragraph(features_list, body_style))
    
    # Page Break for Arabic Section
    elements.append(PageBreak())
    
    # === ARABIC SECTION ===
    elements.append(Paragraph("📊 الملخص بالعربية", heading_style))
    elements.append(Spacer(1, 0.1*inch))
    
    # Overall Status (Arabic)
    elements.append(Paragraph("✅ جميع الأنظمة تعمل بشكل مثالي!", subheading_style))
    elements.append(Paragraph(
        "تُظهر لقطات الشاشة لوحة تحكم <b>MeMo Bot Pro</b> وهي تتتبع أسعار العملات المشفرة "
        "الحية على مدار 4 دقائق (من 06:56 إلى 07:00 UTC). النظام يعمل بالكامل.",
        body_style
    ))
    elements.append(Spacer(1, 0.15*inch))
    
    # 1. Live Updates (Arabic)
    elements.append(Paragraph("1️⃣ تحديثات الأسعار المباشرة تعمل 📈", subheading_style))
    elements.append(Paragraph(
        "النظام يسحب بنجاح <b>البيانات في الوقت الفعلي</b> من Binance API. "
        "الأسعار تتحدث باستمرار كل 30 ثانية:",
        body_style
    ))
    
    price_data_ar = [
        ['العملة', 'نطاق السعر', 'الحالة'],
        ['BTC', '$103,354 - $103,391', '✅ مباشر'],
        ['ETH', '$3,438 - $3,442', '✅ مباشر'],
        ['XRP', '$2.38 - $2.39', '✅ مباشر'],
    ]
    
    price_table_ar = Table(price_data_ar, colWidths=[2*inch, 2*inch, 1.5*inch])
    price_table_ar.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    elements.append(Spacer(1, 0.1*inch))
    elements.append(price_table_ar)
    elements.append(Paragraph(
        "<i>هذه <b>أسعار حقيقية مباشرة</b>، وليست بيانات محاكاة!</i>",
        body_style
    ))
    elements.append(Spacer(1, 0.15*inch))
    
    # 2. All 10 Currencies (Arabic)
    elements.append(Paragraph("2️⃣ لوحة التحكم تعرض جميع العملات الـ 10 ✅", subheading_style))
    elements.append(Paragraph(
        "يتم عرض أفضل 10 عملات مشفرة بنجاح:",
        body_style
    ))
    
    crypto_list_ar = """
    1. BTCUSDT (بيتكوين)<br/>
    2. ETHUSDT (إيثيريوم)<br/>
    3. BNBUSDT (بينانس كوين)<br/>
    4. LTCUSDT (لايتكوين)<br/>
    5. ADAUSDT (كاردانو)<br/>
    6. XRPUSDT (ريبل)<br/>
    7. MATICUSDT (بوليجون)<br/>
    8. DOGEUSDT (دوجكوين)<br/>
    9. SOLUSDT (سولانا)<br/>
    10. DOTUSDT (بولكادوت)
    """
    elements.append(Paragraph(crypto_list_ar, body_style))
    elements.append(Spacer(1, 0.15*inch))
    
    # 3. Health Monitor (Arabic)
    elements.append(Paragraph("3️⃣ حالة مراقبة الصحة 🏥", subheading_style))
    
    health_data_ar = [
        ['المكون', 'الحالة', 'التفاصيل'],
        ['Binance API', '✅ متصل', 'وضع مباشر'],
        ['بوت تليجرام', '✅ متصل', '1 مسؤول'],
        ['الإعدادات', '✅ صالحة', 'جميع البيانات متوفرة'],
        ['موارد النظام', '✅ صحية', 'المعالج والذاكرة طبيعية'],
    ]
    
    health_table_ar = Table(health_data_ar, colWidths=[2*inch, 1.5*inch, 2*inch])
    health_table_ar.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#10b981')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.lightgreen),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    elements.append(health_table_ar)
    elements.append(Spacer(1, 0.15*inch))
    
    # 4. Notifications (Arabic)
    elements.append(Paragraph("4️⃣ جاهز للإشعارات 🔔", subheading_style))
    elements.append(Paragraph(
        "بوت تليجرام يراقب بنشاط هذه العملات الـ 10. عندما يتغير أي سعر بنسبة "
        "<b>1% أو أكثر</b>، سيتلقى <b>المستخدمان المشتركان</b> تنبيهات فورية بالعربية!",
        body_style
    ))
    elements.append(Spacer(1, 0.2*inch))
    
    # Key Features (Arabic)
    elements.append(Paragraph("🎯 الميزات الرئيسية المؤكدة", subheading_style))
    features_list_ar = """
    ✅ تتبع الأسعار في الوقت الفعلي من Binance<br/>
    ✅ عرض جميع العملات الـ 10 الأكثر تداولاً<br/>
    ✅ نظام مراقبة الصحة يعمل<br/>
    ✅ بوت تليجرام متصل ويراقب<br/>
    ✅ مستخدمان مشتركان للإشعارات بالعربية<br/>
    ✅ حد تغير السعر 1% مضبوط<br/>
    ✅ فترة انتظار 5 دقائق لكل عملة لمنع الإزعاج
    """
    elements.append(Paragraph(features_list_ar, body_style))
    elements.append(Spacer(1, 0.3*inch))
    
    # Conclusion
    elements.append(Paragraph("🎯 Conclusion | الخلاصة", heading_style))
    elements.append(Spacer(1, 0.1*inch))
    
    conclusion_table = [
        ['English', 'العربية'],
        ['Everything is working perfectly!', 'كل شيء يعمل بشكل مثالي!'],
        ['Your system is tracking real live prices', 'نظامك يتتبع الأسعار الحية الحقيقية'],
        ['Displaying all 10 currencies', 'يعرض جميع العملات الـ 10'],
        ['Monitoring system health', 'يراقب صحة النظام'],
        ['Ready to send notifications', 'جاهز لإرسال الإشعارات'],
    ]
    
    conclusion_tbl = Table(conclusion_table, colWidths=[2.75*inch, 2.75*inch])
    conclusion_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#764ba2')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.lavender),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    
    elements.append(conclusion_tbl)
    elements.append(Spacer(1, 0.3*inch))
    
    # Final Message
    final_msg = Paragraph(
        "🚀 <b>Your FIRST-TO-MARKET Arabic crypto trading assistant is live and operational!</b>",
        ParagraphStyle(
            'Final',
            parent=body_style,
            fontSize=13,
            textColor=colors.HexColor('#10b981'),
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
    )
    elements.append(final_msg)
    
    # Build PDF
    doc.build(elements)
    print(f"✅ PDF Report generated successfully: {filename}")
    return filename

if __name__ == "__main__":
    create_system_report()
