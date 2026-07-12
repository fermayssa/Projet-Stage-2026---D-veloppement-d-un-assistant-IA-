import { ComponentFixture, TestBed } from '@angular/core/testing';

import { FormViewer } from './form-viewer';

describe('FormViewer', () => {
  let component: FormViewer;
  let fixture: ComponentFixture<FormViewer>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [FormViewer],
    }).compileComponents();

    fixture = TestBed.createComponent(FormViewer);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
