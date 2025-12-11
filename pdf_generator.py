"""
PDF Report Generator for Timesheet Analytics Dashboard
Supports multiple page sizes, orientations, cover pages, and table inclusion
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import A0, A1, A2, A3, A4, A5, A6, LETTER, LEGAL, landscape, portrait
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from datetime import datetime
import io
import plotly.graph_objects as go
import plotly.io as pio
import pandas as pd
import base64

# Page Size Mapping
PAGE_SIZES = {
    'A0': A0,
    'A1': A1,
    'A2': A2,
    'A3': A3,
    'A4': A4,
    'A5': A5,
    'A6': A6,
    'Letter': LETTER,
    'Legal': LEGAL
}

class PDFReportGenerator:
    """Generate comprehensive PDF reports with customizable options"""
    
    def __init__(self, page_size='A4', orientation='Portrait'):
        """
        Initialize PDF generator
        
        Args:
            page_size: One of A0, A1, A2, A3, A4, A5, A6, Letter, Legal
            orientation: 'Portrait' or 'Landscape'
        """
        self.page_size_name = page_size
        self.orientation = orientation
        
        # Get base page size
        base_size = PAGE_SIZES.get(page_size, A4)
        
        # Apply orientation
        if orientation == 'Landscape':
            self.page_size = landscape(base_size)
        else:
            self.page_size = portrait(base_size)
            
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
        
    def _setup_custom_styles(self):
        """Setup custom paragraph styles"""
        # Title Style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1f77b4'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Subtitle Style
        self.styles.add(ParagraphStyle(
            name='CustomSubtitle',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#2ca02c'),
            spaceAfter=12,
            fontName='Helvetica-Bold'
        ))
        
        # Cover Page Title
        self.styles.add(ParagraphStyle(
            name='CoverTitle',
            parent=self.styles['Title'],
            fontSize=36,
            textColor=colors.HexColor('#1f77b4'),
            spaceAfter=50,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
    def create_cover_page(self, title="Timesheet Analytics Report", subtitle=None):
        """
        Create a cover page
        
        Args:
            title: Main title for the report
            subtitle: Optional subtitle
            
        Returns:
            List of flowables for cover page
        """
        story = []
        
        # Add spacing from top
        story.append(Spacer(1, 2*inch))
        
        # Title
        story.append(Paragraph(title, self.styles['CoverTitle']))
        
        # Subtitle if provided
        if subtitle:
            story.append(Paragraph(subtitle, self.styles['CustomSubtitle']))
            
        # Date
        date_str = f"Generated on: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}"
        story.append(Spacer(1, 0.5*inch))
        story.append(Paragraph(date_str, self.styles['Normal']))
        
        # Add metadata
        story.append(Spacer(1, 1*inch))
        metadata = f"""
        <para alignment="center">
        <b>Report Configuration</b><br/>
        Page Size: {self.page_size_name}<br/>
        Orientation: {self.orientation}<br/>
        </para>
        """
        story.append(Paragraph(metadata, self.styles['Normal']))
        
        # Page break after cover
        story.append(PageBreak())
        
        return story
    
    def create_summary_section(self, metrics_dict):
        """
        Create summary metrics section
        
        Args:
            metrics_dict: Dictionary of metric name -> value pairs
            
        Returns:
            List of flowables
        """
        story = []
        
        story.append(Paragraph("Executive Summary", self.styles['CustomTitle']))
        story.append(Spacer(1, 0.3*inch))
        
        # Create table data
        table_data = [['Metric', 'Value']]
        for key, value in metrics_dict.items():
            table_data.append([key, str(value)])
            
        # Create table
        table = Table(table_data, colWidths=[3*inch, 2*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f77b4')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
        ]))
        
        story.append(table)
        story.append(Spacer(1, 0.5*inch))
        
        return story
    
    def create_data_table(self, df, title="Data Table", max_rows=50):
        """
        Create a table from DataFrame
        
        Args:
            df: pandas DataFrame
            title: Table title
            max_rows: Maximum rows to include
            
        Returns:
            List of flowables
        """
        story = []
        
        story.append(Paragraph(title, self.styles['CustomSubtitle']))
        story.append(Spacer(1, 0.2*inch))
        
        # Limit rows
        df_subset = df.head(max_rows)
        
        # Create table data
        table_data = [df_subset.columns.tolist()]
        for _, row in df_subset.iterrows():
            table_data.append([str(val)[:50] for val in row.values])  # Truncate long values
            
        # Create table
        table = Table(table_data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2ca02c')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
        ]))
        
        story.append(table)
        
        if len(df) > max_rows:
            story.append(Spacer(1, 0.1*inch))
            story.append(Paragraph(f"<i>Showing {max_rows} of {len(df)} rows</i>", self.styles['Normal']))
            
        story.append(Spacer(1, 0.3*inch))
        
        return story
    
    def add_chart_image(self, fig, title="Chart", width=6*inch, height=4*inch):
        """
        Convert Plotly figure to image and add to PDF
        Falls back to chart description if image conversion fails
        
        Args:
            fig: Plotly figure object
            title: Chart title
            width: Image width
            height: Image height
            
        Returns:
            List of flowables
        """
        story = []
        
        story.append(Paragraph(title, self.styles['CustomSubtitle']))
        story.append(Spacer(1, 0.2*inch))
        
        try:
            # Try to convert plotly figure to image using kaleido
            img_bytes = pio.to_image(fig, format="png", width=800, height=600, engine="kaleido")
            img = Image(io.BytesIO(img_bytes), width=width, height=height)
            story.append(img)
        except Exception as e:
            # Fallback: Add a note that chart is not available in PDF
            note = f"""
            <para>
            <i>[Chart: {title}]</i><br/>
            <b>Note:</b> Chart visualization is available in the web dashboard.<br/>
            Chart cannot be embedded in PDF due to server limitations.
            </para>
            """
            story.append(Paragraph(note, self.styles['Normal']))
            
        story.append(Spacer(1, 0.3*inch))
        
        return story
    
    def generate_report(self, output_buffer, include_cover=True, sections=None):
        """
        Generate complete PDF report
        
        Args:
            output_buffer: BytesIO buffer to write PDF to
            include_cover: Whether to include cover page
            sections: List of section dictionaries with 'type' and 'data' keys
            
        Returns:
            BytesIO buffer with PDF content
        """
        # Create document
        doc = SimpleDocTemplate(
            output_buffer,
            pagesize=self.page_size,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=0.75*inch,
            bottomMargin=0.75*inch
        )
        
        story = []
        
        # Add cover page
        if include_cover:
            story.extend(self.create_cover_page())
            
        # Add sections
        if sections:
            for section in sections:
                section_type = section.get('type')
                section_data = section.get('data')
                
                if section_type == 'summary':
                    story.extend(self.create_summary_section(section_data))
                elif section_type == 'table':
                    story.extend(self.create_data_table(
                        section_data.get('df'),
                        title=section_data.get('title', 'Data Table'),
                        max_rows=section_data.get('max_rows', 50)
                    ))
                elif section_type == 'chart':
                    story.extend(self.add_chart_image(
                        section_data.get('fig'),
                        title=section_data.get('title', 'Chart')
                    ))
                elif section_type == 'pagebreak':
                    story.append(PageBreak())
                    
        # Build PDF
        doc.build(story)
        
        return output_buffer


def create_timesheet_report(df, metrics, charts, config):
    """
    Helper function to create timesheet analytics report
    
    Args:
        df: Main dataframe
        metrics: Dictionary of summary metrics
        charts: List of plotly figures with titles
        config: Report configuration dict with keys:
            - page_size: str
            - orientation: str
            - include_cover: bool
            - include_tables: list of table names to include
            
    Returns:
        BytesIO buffer with PDF
    """
    # Initialize generator
    generator = PDFReportGenerator(
        page_size=config.get('page_size', 'A4'),
        orientation=config.get('orientation', 'Portrait')
    )
    
    # Build sections
    sections = []
    
    # Summary section
    sections.append({
        'type': 'summary',
        'data': metrics
    })
    
    sections.append({'type': 'pagebreak'})
    
    # Charts
    for chart_info in charts:
        sections.append({
            'type': 'chart',
            'data': {
                'fig': chart_info['fig'],
                'title': chart_info.get('title', 'Chart')
            }
        })
        
    # Tables
    include_tables = config.get('include_tables', [])
    if 'raw_data' in include_tables and df is not None:
        sections.append({'type': 'pagebreak'})
        sections.append({
            'type': 'table',
            'data': {
                'df': df,
                'title': 'Raw Timesheet Data',
                'max_rows': 100
            }
        })
        
    # Generate report
    buffer = io.BytesIO()
    generator.generate_report(
        buffer,
        include_cover=config.get('include_cover', True),
        sections=sections
    )
    
    buffer.seek(0)
    return buffer
