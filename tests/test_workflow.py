import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

SCRIPT=Path(__file__).resolve().parents[1]/'skills/launch-video/scripts/launch_video.py'
spec=importlib.util.spec_from_file_location('launch_video',SCRIPT)
w=importlib.util.module_from_spec(spec);spec.loader.exec_module(w)

class WorkflowTests(unittest.TestCase):
    def setUp(self):
        t=tempfile.TemporaryDirectory();self.addCleanup(t.cleanup);self.root=Path(t.name)
        (self.root/'frames').mkdir();self.frame=self.root/'frames/one.html'
        self.frame.write_text('<h1>One clear next step.</h1>')
        self.data={'schemaVersion':1,'product':{'name':'Test fixture','fictional':True,'summary':'Fictional workflow.','audience':'Test users','promise':'One next step','cta':'Try fixture'},'direction':'Clear demonstration.','brand':{'basis':'Fictional fixture','font':'Arial, sans-serif','colors':{'ink':'#111111'}},'video':{'width':1920,'height':1080,'fps':30,'audio':'none'},'scenes':[{'id':'one','duration':1,'copy':'One clear next step.','narration':'','motion':'Focus on one card.','frame':'frames/one.html','assets':[]}]};self.save()
    def save(self): (self.root/'project.json').write_text(json.dumps(self.data))
    def approve(self):
        p=w.prepare(self.root);w.record_approval(self.root,p['version'],'UNIT TEST ONLY','Simulated approval of disposable fixture, never showcase.');return p
    def composition(self):
        (self.root/'scene.html').write_text('<template><div data-composition-id="one">'+self.frame.read_text()+'</div></template>')
        (self.root/'index.html').write_text('<div data-composition-id="fixture" data-width="1920" data-height="1080" data-duration="1"><div id="one" data-composition-id="one" data-composition-src="scene.html" data-start="0" data-duration="1"></div></div>')
    def test_composition_metadata_title_is_not_visible_copy(self):
        self.frame.write_text('<title>Static review</title><h1>One clear next step.</h1>')
        self.approve();self.composition()
        (self.root/'scene.html').write_text('<template><div data-composition-id="one"><h1>One clear next step.</h1></div></template>')
        w.verify_composition(self.root,self.data)
    def test_scene_copy_and_timing_drift_rejected(self):
        self.approve();self.composition()
        (self.root/'scene.html').write_text('<div data-composition-id="one"><h1>Unapproved promise</h1></div>')
        with self.assertRaisesRegex(ValueError,'Scene text differs'): w.verify_composition(self.root,self.data)
        self.composition();p=self.root/'index.html';p.write_text(p.read_text().replace('data-start="0"','data-start="0.5"'))
        with self.assertRaisesRegex(ValueError,'Scene timing differs'): w.verify_composition(self.root,self.data)
    def test_mismatched_scene_mount_cannot_render_blank_video(self):
        self.approve();self.composition()
        path=self.root/'scene.html';path.write_text(path.read_text().replace('data-composition-id="one"','data-composition-id="wrong"'))
        with patch.object(w,'run') as run:
            with self.assertRaisesRegex(ValueError,'mount and subcomposition IDs'): w.render(self.root,'demo.mp4')
            run.assert_not_called()
    def test_self_contained_designed_storyboard(self):
        p=w.prepare(self.root);page=(self.root/'storyboard.html').read_text()
        self.assertIn('srcdoc=',page);self.assertIn('One clear next step.',page);self.assertIn('Fictional demonstration product',page)
        self.assertEqual(w.sha(page.encode()),p['sha256'])
    def test_sparse_input_names_missing_fact(self):
        del self.data['product']['promise'];self.save()
        with self.assertRaisesRegex(ValueError,'product.promise'): w.prepare(self.root)
    def test_missing_and_outside_asset(self):
        self.frame.unlink()
        with self.assertRaisesRegex(ValueError,'Missing project asset'): w.prepare(self.root)
        self.data['scenes'][0]['frame']=str(SCRIPT);self.save()
        with self.assertRaisesRegex(ValueError,'outside project'): w.prepare(self.root)
    def test_remote_asset_rejected_local_asset_embedded(self):
        self.frame.write_text('<h1>One clear next step.</h1><img src="https://example.com/photo.png">')
        with self.assertRaisesRegex(ValueError,'local and listed'): w.prepare(self.root)
        (self.root/'pixel.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg" width="1" height="1"/>')
        self.data['scenes'][0]['assets']=['pixel.svg'];self.save()
        self.frame.write_text('<h1>One clear next step.</h1><img src="../pixel.svg">');w.prepare(self.root)
        self.assertIn('data:image/svg+xml;base64,',(self.root/'storyboard.html').read_text())
    def test_unquoted_resources_rejected_before_storyboard_write(self):
        for src in ('https://example.invalid/logo.svg', '../local.svg'):
            self.frame.write_text(f'<h1>One clear next step.</h1><img src={src}>')
            with self.assertRaisesRegex(ValueError,'Unquoted src'): w.prepare(self.root)
            self.assertFalse((self.root/'storyboard.html').exists())
    def test_external_svg_resource_cannot_escape_approval_hash(self):
        for tag,attr,url in [('image','href','https://example.invalid/image.png'),('use','xlink:href','../icons.svg#mark'),('feImage','href','https://example.invalid/filter.svg')]:
            self.frame.write_text(f'<h1>One clear next step.</h1><svg><{tag} {attr}="{url}"/></svg>')
            with self.assertRaisesRegex(ValueError,'SVG resource href'): w.prepare(self.root)
            self.assertFalse((self.root/'storyboard.html').exists())
        self.frame.write_text('<h1>One clear next step.</h1><svg><defs><path id="mark" d="M0 0"/></defs><use href="#mark"/></svg>')
        w.prepare(self.root)
    def test_missing_approval_never_launches_render(self):
        w.prepare(self.root)
        with patch.object(w,'run') as run:
            with self.assertRaisesRegex(ValueError,'approval is required'): w.render(self.root,'demo.mp4')
            run.assert_not_called()
    def test_revision_invalidates_approval_preserves_previous(self):
        old=self.approve();path=self.root/'storyboards'/f'{old["version"]}.html';saved=path.read_bytes()
        self.data['scenes'][0]['copy']='A refined next step.';self.save();self.frame.write_text('<h1>A refined next step.</h1>')
        new=w.prepare(self.root);self.assertNotEqual(old['version'],new['version']);self.assertEqual(saved,path.read_bytes())
        with self.assertRaisesRegex(ValueError,'approval is required'): w.check_approval(self.root)
    def test_changed_frame_or_storyboard_is_stale(self):
        self.approve();(self.root/'storyboard.html').write_text('tampered')
        with self.assertRaisesRegex(ValueError,'stale'): w.check_approval(self.root)
        w.prepare(self.root);self.frame.write_text('<h1>One clear next step.</h1><p>New claim</p>')
        with self.assertRaisesRegex(ValueError,'stale'): w.check_approval(self.root)
    def test_exact_version_and_statement_required(self):
        p=w.prepare(self.root)
        with self.assertRaisesRegex(ValueError,'does not match'): w.record_approval(self.root,'wrong','CJ','Approved')
        with self.assertRaisesRegex(ValueError,'approval statement'): w.record_approval(self.root,p['version'],'CJ','')
    def test_render_failure_has_actionable_error_no_success_receipt(self):
        self.approve();self.composition()
        with patch.object(w.subprocess,'run',side_effect=w.subprocess.CalledProcessError(1,['npx'],stderr='Missing image: logo.png')):
            with self.assertRaisesRegex(ValueError,'Missing image: logo.png'): w.render(self.root,'demo.mp4')
        self.assertFalse((self.root/'demo.qa.json').exists())
    def test_technical_success_does_not_claim_visual_qa(self):
        self.approve();self.composition()
        metadata={'streams':[{'codec_type':'video','codec_name':'h264','width':1920,'height':1080,'avg_frame_rate':'30/1'}],'format':{'duration':'1.0'}}
        def runner(cmd,root):
            if cmd[0]=='ffprobe': return json.dumps(metadata)
            if 'render' in cmd: Path(cmd[-1]).write_bytes(b'TEST ONLY')
            return ''
        with patch.object(w,'run',side_effect=runner): r=w.render(self.root,'demo.mp4')
        self.assertIn('pending',r['visualQA']);self.assertTrue((self.root/'demo.qa.json').exists())
    def test_export_mismatch_rejected(self):
        self.approve();self.composition()
        metadata={'streams':[{'codec_type':'video','codec_name':'h264','width':1280,'height':720,'avg_frame_rate':'30/1'}],'format':{'duration':'1.0'}}
        with patch.object(w,'run',return_value=json.dumps(metadata)):
            with self.assertRaisesRegex(ValueError,'specifications do not match'): w.render(self.root,'demo.mp4')
        self.assertFalse((self.root/'demo.qa.json').exists())

if __name__=='__main__': unittest.main()
